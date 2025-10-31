import {
  getFieldName,
  isPrimitive,
  isString,
  useAlert,
} from "@maykin-ui/admin-ui";
import { invariant } from "@maykin-ui/client-common/assert";
import { useCallback, useEffect, useMemo, useState } from "react";
import { useActionData } from "react-router";
import { TypedAction } from "~/hooks/useSubmitAction.tsx";
import { TabConfig } from "~/pages";
import { ZaaktypeAction } from "~/pages/zaaktype/zaaktype.action.ts";
import { Expanded, RelatedObject } from "~/types";

/**
 * Maps each tab key (or related object key) to an array of field-level errors
 * related to a specific related object.
 */
export type RelatedFieldErrorsByTab<T extends object> = Partial<
  Record<string, RelatedErrors<T>>
>;

/**
 * List of field-level errors for an expanded related target type.
 */
export type RelatedErrors<T extends object> = Errors<Expanded<T>>[];

/**
 * Maps each tab key to a set of field-level errors that are not related
 * to nested or related objects.
 */
export type NonRelatedFieldErrorsByTab<T extends object> = Partial<
  Record<string, NonRelatedErrors<T>>
>;

/**
 * Field-level errors for the main (non-related) target type.
 */
export type NonRelatedErrors<T extends object> = Errors<T>;

/**
 * Maps non-field-level errors (errors not tied to specific fields)
 * to each tab key in the configuration.
 */
export type NonFieldErrorsByTab<T extends object> = Partial<
  Record<keyof T, string>
>;

export type FunctionWrap = (fn: WrappedFunction) => WrappedFunction;

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type WrappedFunction = (...args: any[]) => unknown;

/**
 * Aggregates and manages all error types related to a Zaaktype object and its tabs.
 *
 * This hook:
 * - Collects and synchronizes non-field, related-field, and non-related-field errors
 *   derived from backend validation results.
 * - Keeps these errors in React state to prevent unintended clearing between tab switches.
 * - Provides a utility `clearErrorsOn(fn)` that wraps a function and clears all
 *   tracked error states before executing it.
 *
 * @typeParam T - The base object type (e.g. Zaaktype).
 * @typeParam A - The typed action associated with backend interactions.
 * @param object - The current object instance being edited.
 * @param tabConfigs - The tab configuration array describing how fields are grouped.
 * @returns A tuple containing:
 *  1. `nonFieldErrorsState`: errors related to entire tabs or relations.
 *  2. `relatedFieldErrorsByTabState`: errors for nested related objects (arrays/grids).
 *  3. `nonRelatedFieldErrorsByTabState`: errors for direct fields on the object.
 *  4. `clearErrorsOn`: a memoized function wrapper that resets error states.
 */
export function useErrorsState<T extends object, A extends TypedAction>(
  object: Expanded<T>,
  tabConfigs: TabConfig<T>[],
): [
  NonFieldErrorsByTab<T>,
  RelatedFieldErrorsByTab<T>,
  NonRelatedFieldErrorsByTab<T>,
  FunctionWrap,
] {
  // Create a record that matches every relatedObjectKey/tabKey with a non-field error string.
  const nonFieldErrorsByTab = useNonFieldErrors<T, A>(object, tabConfigs);

  // Create a record that matches every relatedObjectKey/tabKey with an `Errors[]` array.
  const relatedFieldErrorsByTab = useRelatedFieldErrors<T, A>(object);

  // Create a record that matches every relatedObjectKey/tabKey with an `Errors[]` array.
  const nonRelatedFieldErrorsByTab = useNonRelatedFieldErrors(
    object,
    tabConfigs,
  );

  // Store NonFieldErrorsByTab record in state.
  const [nonFieldErrorsState, setNonFieldErrorsState] =
    useState(nonFieldErrorsByTab);

  // Sync FieldErrorsByTab record.
  useEffect(() => {
    // Only update, don't clear (automatically).
    // This prevents clearing errors on tab change.
    if (Object.keys(nonFieldErrorsByTab).length) {
      setNonFieldErrorsState(nonFieldErrorsByTab);
    }
  }, [nonFieldErrorsByTab]);

  // Store `relatedFieldErrorsByTab` record in state.
  const [relatedFieldErrorsByTabState, setRelatedFieldErrorsByTabState] =
    useState(relatedFieldErrorsByTab);

  // Sync `relatedFieldErrorsByTabState`.
  useEffect(() => {
    // Only update, don't clear (automatically).
    // This prevents clearing errors on tab change.
    if (Object.keys(relatedFieldErrorsByTab).length) {
      setRelatedFieldErrorsByTabState(relatedFieldErrorsByTab);
    }
  }, [relatedFieldErrorsByTab]);

  // Store `relatedFieldErrorsByTab` record in state.
  const [nonRelatedFieldErrorsByTabState, setNonRelatedFieldErrorsByTabState] =
    useState(nonRelatedFieldErrorsByTab);

  // Sync `nonRelatedFieldErrorsByTabState`.
  useEffect(() => {
    // Only update, don't clear (automatically).
    // This prevents clearing errors on tab change.
    if (Object.keys(nonRelatedFieldErrorsByTab).length) {
      setNonRelatedFieldErrorsByTabState(nonRelatedFieldErrorsByTab);
    }
  }, [nonRelatedFieldErrorsByTab]);

  /**
   * Returns a memoized wrapper around `fn` that clears
   * `nonFieldErrorsState` and `relatedFieldErrorsByTabState` before calling it.
   *
   * @param fn - The function to wrap.
   * @returns A stable callback that clears errors and then calls `fn`.
   */
  const clearErrorsOn = useCallback<FunctionWrap>(
    (fn) =>
      (...args) => {
        setNonFieldErrorsState({});
        setRelatedFieldErrorsByTabState({});
        return fn(...args);
      },
    [],
  );

  return [
    nonFieldErrorsState,
    relatedFieldErrorsByTabState,
    nonRelatedFieldErrorsByTabState,
    clearErrorsOn,
  ];
}

/**
 * Collects and maps non-field-level errors to tabs based on the provided
 * tab configuration. Used for actions affecting the entire target type hierarchy.
 *
 * @typeParam T - The base object type (e.g. Zaaktype).
 * @typeParam A - The typed action associated with backend interactions.
 * @param object - The target object containing related entities.
 * @param tabConfigs - The list of tab configurations defining the form layout.
 * @returns A memoized mapping of non-field errors by tab key.
 */
export function useNonFieldErrors<T extends object, A extends TypedAction>(
  object: T,
  tabConfigs: TabConfig<T>[],
) {
  const errorTuples = useErrors<T | RelatedObject<T>, A>(undefined, false);

  return useMemo(() => {
    return errorTuples.reduce<NonFieldErrorsByTab<T>>((acc, [, errors]) => {
      // Search for errors based on tabConfig keys.
      // - Applicable to actions acting on entire ZaakType hierarchy (e.g. "PUBLISH_VERSION").
      // - Relevant for non-nested errors relating to directly to a relation.
      // - Action does not have a relatedObjectKey.
      // - Errors relate to relation expressed by tab, not to nested fields.
      tabConfigs.forEach((tabConfig) => {
        const key = tabConfig.key;
        if (key in errors) {
          invariant(key in object, "key not key in object!");
          invariant(key in errors, "key is not key in errors!");
          acc[key as keyof T] = errors[key as keyof typeof errors];
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
 * @typeParam T - The base object type (e.g. Zaaktype).
 * @typeParam A - The typed action associated with backend interactions.
 * @param object - The target object containing related entities.
 * @returns A memoized mapping of related field errors by tab key.
 */
export function useRelatedFieldErrors<T extends object, A extends TypedAction>(
  object: Expanded<T>,
) {
  const errorTuples = useErrors<T | RelatedObject<T>, A>(undefined, false);

  return useMemo<RelatedFieldErrorsByTab<T>>(
    () =>
      errorTuples.reduce((acc, [action]) => {
        // Search for errors based on the relatedObjectKey in action payload
        // - Applicable to actions acting on related objects (e.g. "ADD_RELATED_OBJECT").
        // - Relevant for related objects in DataGrids.
        // - Action explicitly sets tab.
        // - Array of errors is returned matching each row in DataGrid.
        // - Errors relate to fields within tab rather than relation expressed by tab.
        if (
          !isPrimitive(action.payload) &&
          "relatedObjectKey" in action.payload
        ) {
          const key = action.payload.relatedObjectKey;
          invariant(isString(key), "key is not a string!");
          invariant(key in object._expand, "key is not key in object!");

          const relatedObject = object._expand[key];

          if (relatedObject) {
            const length = Object.keys(relatedObject).length;

            const siblings = errorTuples.filter(([sAction]) => {
              return (
                !isPrimitive(sAction.payload) &&
                "relatedObjectKey" in sAction.payload &&
                sAction.payload.relatedObjectKey === key
              );
            });

            return {
              ...acc,
              [key]: errorPerRow<T, A>(siblings, length),
            };
          }
        }
        return acc;
      }, {}),
    [errorTuples, object],
  );
}

/**
 * Collects and maps non-related field-level errors (errors directly on the
 * main object) to tabs based on the tab configuration.
 *
 * @typeParam T - The base object type (e.g. Zaaktype).
 * @typeParam A - The typed action associated with backend interactions.
 * @param object - The main object being validated.
 * @param tabConfigs - The list of tab configurations defining the form layout.
 * @returns A memoized mapping of non-related field errors by tab key.
 */
export function useNonRelatedFieldErrors<
  T extends object,
  A extends ZaaktypeAction,
>(object: T, tabConfigs: TabConfig<T>[]) {
  const errorTuples = useErrors<T | RelatedObject<T>, A>(undefined, false);

  return useMemo(
    () =>
      errorTuples.reduce<NonRelatedFieldErrorsByTab<T>>(
        (acc, [action, errors]) => {
          if ("relatedObjectKey" in action.payload) {
            return acc;
          }

          // Search for errors based on tabConfig keys.
          // - Applicable to actions acting on ZaakType (e.g. "UPDATE_VERSION").
          // - Relevant for errors on ZaakType fields.
          // - Errors relate to ZaakType fields directly.
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
                const current = acc[key] ?? {};

                acc[key] = {
                  ...current,
                  [tabConfigField]:
                    errors[tabConfigField as keyof typeof errors],
                };
              }
            }
          }
          return acc;
        },
        {},
      ),
    [errorTuples, object],
  );
}

/**
 * Return `Errors[]` of `size`, each object sits position indicated `ZaaktypeAction` found in
 * `errorTuples[number][0].payload.rowIndex`.
 * @typeParam T - The base object type (e.g. Zaaktype).
 * @typeParam A - The typed action associated with backend interactions.
 */
function errorPerRow<T extends object, A extends TypedAction>(
  errorTuples: [A, Errors<RelatedObject<T>>][],
  size: number,
): Errors<T>[] {
  return errorTuples.reduce((acc, [action, errors]) => {
    const payload = action.payload;
    if (payload && !isPrimitive(payload) && "rowIndex" in payload) {
      const rowIndex = payload.rowIndex;
      invariant(typeof rowIndex === "number", "rowIndex is not a number!");
      acc[rowIndex] = errors;
      return acc;
    } else {
      return acc;
    }
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
