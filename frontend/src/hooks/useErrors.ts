import { isPrimitive, useAlert } from "@maykin-ui/admin-ui";
import { invariant } from "@maykin-ui/client-common/assert";
import { useActionData } from "react-router";
import { TypedAction } from "~/hooks/useSubmitAction.tsx";

export type ErrorDataTuple<A extends TypedAction = TypedAction> = [A, object];
export type ErrorTuple<A extends TypedAction = TypedAction> = [A, Errors];
export type Errors<T extends object = object> = Partial<
  Record<keyof T, string>
>;

export type ErrorMatcher<
  T extends object = object,
  A extends TypedAction = TypedAction,
> = (action: ErrorTuple<A>[0], errors: Errors<T>) => boolean;

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
>(matcher?: ErrorMatcher<T, A>, flat?: true): Errors;
export function useErrors<
  T extends object = object,
  A extends TypedAction = TypedAction,
>(matcher?: ErrorMatcher<T, A>, flat?: false): ErrorTuple<A>[];
export function useErrors<
  T extends object = object,
  A extends TypedAction = TypedAction,
>(matcher?: ErrorMatcher<T, A>, flat = true): Errors | ErrorTuple<A>[] {
  const alert = useAlert();
  const actionData =
    useActionData() ||
    ([] as ErrorDataTuple<A> | ErrorDataTuple<A>[] | undefined);

  // No action data returned → no errors
  if (!actionData) {
    return flat ? {} : [];
  }

  // Validate that actionData is an array
  invariant(
    Array.isArray(actionData),
    "actionData should either be a [TypedAction, object] or a [TypedAction, object][]!",
  );

  // Detect whether we received a batch of tuples or a single tuple
  const isBatch = isErrorTupleArray<A>(actionData);

  // Normalize into an array of tuples
  const errorDataTuples = isBatch
    ? actionData
    : ([actionData] as [A, object][]);

  // Map each action tuple to its parsed errors
  const errorTuples = errorDataTuples.map<[A, Errors]>(
    ([action, errorData]) => {
      const errors = errorData2Errors(errorData) || {};

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
    return filteredErrorTuples.reduce<Errors>((acc, [, errors]) => {
      return { ...acc, ...errors };
    }, {});
  }
  return filteredErrorTuples;
}

/**
 * Type guard that checks if the input is an array of ErrorTuple.
 */
function isErrorTupleArray<A extends TypedAction = TypedAction>(
  errorTupleOrTuples: ErrorDataTuple<A> | ErrorDataTuple<A>[],
): errorTupleOrTuples is ErrorDataTuple<A>[] {
  return Array.isArray(errorTupleOrTuples);
}

/**
 * Converts error data to a key-value object of field names to reasons.
 *
 * Returns `false` if the error data cannot be parsed.
 */
function errorData2Errors(errorData: object): Errors | false {
  if ("invalidParams" in errorData && Array.isArray(errorData.invalidParams)) {
    return errorData.invalidParams.reduce((acc, invalidParam) => {
      // Validate structure of invalidParam
      invariant(!isPrimitive(invalidParam), "invalidParam is not an object!");
      invariant("name" in invalidParam, "invalidParam incorrectly formatted");
      invariant("reason" in invalidParam, "invalidParam incorrectly formatted");

      // Accumulate errors as { fieldName: reason }
      return { ...acc, [invalidParam.name]: invalidParam.reason };
    }, {});
  }

  // Return false if errorData cannot be parsed
  return false;
}
