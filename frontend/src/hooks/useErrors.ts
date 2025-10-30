import { getFieldName, isPrimitive, useAlert } from "@maykin-ui/admin-ui";
import { invariant } from "@maykin-ui/client-common/assert";
import { useMemo } from "react";
import { useActionData } from "react-router";
import { TypedAction } from "~/hooks/useSubmitAction.tsx";
import { TabConfig, TargetType } from "~/pages";
import { ZaaktypeAction } from "~/pages/zaaktype/zaaktype.action.ts";
import { Expanded, RelatedObject } from "~/types";

/**
 * Maps each tab key (or related object key) to an array of field-level errors
 * related to a specific related object.
 */
export type RelatedFieldErrorsByTab = Partial<{
  [index: string]: RelatedErrors;
}>;

/**
 * List of field-level errors for an expanded related target type.
 */
export type RelatedErrors = Errors<Expanded<TargetType>>[];

/**
 * Maps each tab key to a set of field-level errors that are not related
 * to nested or related objects.
 */
export type NonRelatedFieldErrorsByTab = Partial<{
  [index: string]: NonRelatedErrors;
}>;

/**
 * Field-level errors for the main (non-related) target type.
 */
export type NonRelatedErrors = Errors<TargetType>;

/**
 * Maps non-field-level errors (errors not tied to specific fields)
 * to each tab key in the configuration.
 */
export type NonFieldErrorsByTab = Partial<{
  [index in keyof TargetType]: string;
}>;

/**
 * Collects and maps non-field-level errors to tabs based on the provided
 * tab configuration. Used for actions affecting the entire target type hierarchy.
 *
 * @param tabConfigs - The list of tab configurations defining the form layout.
 * @returns A memoized mapping of non-field errors by tab key.
 */
export function useNonFieldErrors(tabConfigs: TabConfig<TargetType>[]) {
  const errorTuples = useErrors<
    TargetType | RelatedObject<TargetType>,
    ZaaktypeAction
  >(undefined, false);

  return useMemo<NonFieldErrorsByTab>(() => {
    return errorTuples.reduce<NonFieldErrorsByTab>((acc, [, errors]) => {
      // Search for errors based on tabConfig keys.
      // - Applicable to actions acting on entire ZaakType hierarchy (e.g. "PUBLISH_VERSION").
      // - Relevant for non-nested errors relating to directly to a relation.
      // - Action does not have a relatedObjectKey.
      // - Errors relate to relation expressed by tab, not to nested fields.
      tabConfigs.forEach((tabConfig) => {
        const _key = tabConfig.key;
        if (_key in errors) {
          const key = _key as keyof (TargetType | RelatedObject<TargetType>);
          acc[key] = errors[key];
        }
      });
      return acc;
    }, {});
  }, [errorTuples]);
}

/**
 * Collects and maps related field-level errors to tabs based on
 * related object keys found in the action payload.
 *
 * @param object - The target object containing related entities.
 * @returns A memoized mapping of related field errors by tab key.
 */
export function useRelatedFieldErrors(object: TargetType) {
  const errorTuples = useErrors<
    TargetType | RelatedObject<TargetType>,
    ZaaktypeAction
  >(undefined, false);

  return useMemo<RelatedFieldErrorsByTab>(
    () =>
      errorTuples.reduce((acc, [action]) => {
        // Search for errors based on the relatedObjectKey in action payload
        // - Applicable to actions acting on related objects (e.g. "ADD_RELATED_OBJECT").
        // - Relevant for related objects in DataGrids.
        // - Action explicitly sets tab.
        // - Errors relate to fields within tab rather than relation expressed by tab.
        if ("relatedObjectKey" in action.payload) {
          const key = action.payload.relatedObjectKey;
          const relatedObject = object._expand[key];

          if (relatedObject) {
            const length = Object.keys(relatedObject).length;

            const siblings = errorTuples.filter(([sAction]) => {
              return (
                "relatedObjectKey" in sAction.payload &&
                sAction.payload.relatedObjectKey === key
              );
            });

            return {
              ...acc,
              [key]: errorPerRow(siblings, length),
            };
          }
        }
        return acc;
      }, {}),
    [errorTuples, object, errorPerRow],
  );
}

/**
 * Collects and maps non-related field-level errors (errors directly on the
 * main object) to tabs based on the tab configuration.
 *
 * @param tabConfigs - The list of tab configurations defining the form layout.
 * @param object - The main object being validated.
 * @returns A memoized mapping of non-related field errors by tab key.
 */
export function useNonRelatedFieldErrors(
  tabConfigs: TabConfig<TargetType>[],
  object: TargetType,
) {
  const errorTuples = useErrors<
    TargetType | RelatedObject<TargetType>,
    ZaaktypeAction
  >(undefined, false);

  return useMemo<NonRelatedFieldErrorsByTab>(
    () =>
      errorTuples.reduce((acc, [action, errors]) => {
        if ("relatedObjectKey" in action.payload) {
          return acc;
        }

        // Search for errors based on tabConfig keys.
        // - Applicable to actions acting on ZaakType (e.g. "UPDATE_VERSION").
        // - Relevant for errors on ZaakType fields.
        // - Errors relate to ZaakType fields directly.
        const _acc: NonRelatedFieldErrorsByTab = { ...acc };
        for (const tabConfig of tabConfigs) {
          if (tabConfig.view !== "AttributeGrid") continue;

          const key = tabConfig.key;
          const tabConfigFields = tabConfig.sections.flatMap((section) =>
            section.fieldsets.flatMap((fieldset) =>
              fieldset[1].fields.map((field) => getFieldName(field)),
            ),
          );

          for (const tabConfigField of tabConfigFields) {
            if (
              tabConfigField in object &&
              !Array.isArray(object[tabConfigField]) &&
              tabConfigField in errors
            ) {
              const errs = errors as NonRelatedErrors;
              const current = _acc[key] ?? {};
              _acc[key] = {
                ...current,
                [tabConfigField]: errs[tabConfigField],
              };
            }
          }
        }
        return _acc;
      }, {}),
    [errorTuples, object, errorPerRow],
  );
}

/**
 * Return `Errors[]` of `size`, each object sits position indicated `ZaaktypeAction` found in
 * `errorTuples[number][0].payload.rowIndex`.
 */
function errorPerRow(
  errorTuples: [ZaaktypeAction, Errors<RelatedObject<TargetType>>][],
  size: number,
): Errors<TargetType>[] {
  return errorTuples.reduce((acc, [action, errors]) => {
    if (!action || !action.payload || !("rowIndex" in action.payload))
      return acc;

    acc[action.payload.rowIndex] = errors;
    return acc;
  }, new Array(size).fill({}));
}

export type ErrorDataTuple<A extends TypedAction = TypedAction> = [A, object];
export type ErrorTuple<
  A extends TypedAction = TypedAction,
  T extends object = object,
> = [A, Errors<T>];
export type Errors<T extends object = object> = Partial<
  Record<keyof T, string>
>;

export type ErrorMatcher<
  T extends object = object,
  A extends TypedAction = TypedAction,
> = (action: ErrorTuple<A, T>[0], errors: Errors<T>) => boolean;

/**
 * Custom hook that extracts and normalizes errors from action data.
 *
 * Returns an array of `[TypedAction, errors]` tuples if errors exist,
 * or `undefined` if no action data is returned.
 * Shows an alert if an error object cannot be parsed.
 */
export function useErrors<
  T extends object = object,
  A extends TypedAction = TypedAction,
>(matcher?: ErrorMatcher<T, A>, flat?: true): Errors<T>;
export function useErrors<
  T extends object = object,
  A extends TypedAction = TypedAction,
>(matcher?: ErrorMatcher<T, A>, flat?: false): ErrorTuple<A, T>[];
export function useErrors<
  T extends object = object,
  A extends TypedAction = TypedAction,
>(matcher?: ErrorMatcher<T, A>, flat = true): Errors<T> | ErrorTuple<A, T>[] {
  const alert = useAlert();
  const actionData = useActionData();

  return useMemo(() => {
    const normalizedActionData = actionData || ([] as ErrorDataTuple<A>[]);

    // Validate that actionData is an array
    invariant(
      Array.isArray(normalizedActionData),
      "actionData should either be a [TypedAction, object] or a [TypedAction, object][]!",
    );

    // Detect whether we received a batch of tuples or a single tuple
    const isBatch = isErrorTupleArray<A>(normalizedActionData);

    // Normalize into an array of tuples
    const errorDataTuples = isBatch
      ? normalizedActionData
      : Array.isArray(normalizedActionData) && normalizedActionData.length
        ? ([normalizedActionData] as [A, object][])
        : [];

    // Map each action tuple to its parsed errors
    const errorTuples = errorDataTuples.map<[A, Errors<T>]>(
      ([action, errorData]) => {
        const errors = errorData2Errors<T>(errorData) || {};

        // If parsing failed, show alert with raw error data
        if (!errors) {
          alert("Foutmelding", JSON.stringify(errorData), "Ok");
        }

        return [action, errors];
      },
    );

    // If matcher is set, only use errors that match.
    const filteredErrorTuples = matcher
      ? errorTuples.filter((tuple) => matcher(...tuple))
      : errorTuples;

    // Reduce ErrorTuple to Errors.
    if (flat) {
      return filteredErrorTuples.reduce<Errors<T>>((acc, [, errors]) => {
        return { ...acc, ...errors };
      }, {});
    }

    return filteredErrorTuples;
  }, [actionData, matcher, flat]);
}

/**
 * Type guard that checks if the input is an array of ErrorTuple.
 */
function isErrorTupleArray<A extends TypedAction = TypedAction>(
  errorTupleOrTuples: ErrorDataTuple<A> | ErrorDataTuple<A>[],
): errorTupleOrTuples is ErrorDataTuple<A>[] {
  return (
    Array.isArray(errorTupleOrTuples) && Array.isArray(errorTupleOrTuples[0])
  );
}

/**
 * Converts error data to a key-value object of field names to reasons.
 *
 * Returns `false` if the error data cannot be parsed.
 */
function errorData2Errors<T extends object = object>(
  errorData: object,
): Errors<T> | false {
  if ("invalidParams" in errorData && Array.isArray(errorData.invalidParams)) {
    return errorData.invalidParams.reduce((acc, invalidParam) => {
      // Validate structure of invalidParam
      invariant(!isPrimitive(invalidParam), "invalidParam is not an object!");
      invariant("name" in invalidParam, "invalidParam incorrectly formatted");
      invariant("reason" in invalidParam, "invalidParam incorrectly formatted");

      // Accumulate errors as { fieldName: reason }
      return { ...acc, [invalidParam.name]: invalidParam.reason };
    }, {} as Errors<T>);
  }

  // Return false if errorData cannot be parsed
  return false;
}
