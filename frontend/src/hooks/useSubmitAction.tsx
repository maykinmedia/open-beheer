import { Errors, useAlert } from "@maykin-ui/admin-ui";
import { useEffect } from "react";
import { SubmitOptions, useActionData, useSubmit } from "react-router";
import { collectErrorMessages } from "~/lib";

// From React Router
export type JsonObject = {
  [Key in string]: JsonValue;
} & {
  [Key in string]?: JsonValue | undefined;
};
export type JsonArray = JsonValue[] | readonly JsonValue[];
export type JsonPrimitive = string | number | boolean | null;
export type JsonValue = JsonPrimitive | JsonObject | JsonArray;

/**
 * Can be used when using (React Router) actions to explicitly set the type
 * of action, and it's payload. This is similar to a Redux action.
 *
 * @example
 *
 *   const increment: TypedAction = \{
 *     type: "INCREMENT_VALUE",
 *     payload: 1
 *   \}
 *
 * NOTE: Using complex objects in (React Router) `submit()` calls require a method
 * to be set and an encType of "application/json" to be used.
 *
 * @example
 *   const submit = useSubmit()
 *
 *   submit(increment, \{
 *       method: "POST",  // NOTE: Not needed when using `submitAction()`.
 *       encType: "application/json",  // NOTE: Not needed when using `submitAction()`.
 *   \})
 */
export type TypedAction<T = string, P = JsonValue> = {
  type: T;
  payload: P;
};

/**
 * A small wrapper around React Routers' `useSubmit()` that takes a `TypedAction`
 * as data. The `SubmitOptions` default to method of "POST" and an encType of "application/json".
 *
 * @example
 *   const submitAction = useSubmitAction();
 *
 *   const increment: TypedAction = \{
 *     type: "INCREMENT_VALUE",
 *     payload: 1
 *   \}
 *
 *   submitAction(increment);
 *
 * NOTE: In the (React Router) action handler `request.clone().json()` should be
 * used to retrieve the `TypedAction`. If multiple actions should be handled the
 * type of the action can be used to determine the applicable logic.
 */
export function useSubmitAction<T extends TypedAction = TypedAction>(
  catchErrors: boolean = true,
) {
  const submit = useSubmit();
  const actionData = useActionData() as object;
  const alert = useAlert();

  // Show error(s) if present.
  useEffect(() => {
    if (catchErrors && actionData) {
      let messages;
      if (
        "invalidParams" in actionData &&
        Array.isArray(actionData.invalidParams)
      ) {
        messages = actionData.invalidParams.map(({ name, reason }) =>
          [name, reason].join(": "),
        );
      } else {
        const collectedMessages = collectErrorMessages(actionData);
        messages = collectedMessages.length
          ? collectedMessages
          : "Er is een onbekende fout opgetreden.";
      }

      alert(
        "Foutmelding",
        (<Errors errors={messages} />) as unknown as string, // TODO: Fix in admin-ui
        "Ok",
      );
    }
  }, [actionData, catchErrors]);

  return (typedAction: T, options: SubmitOptions = {}) => {
    const targetOptions: SubmitOptions = {
      method: "POST",
      encType: "application/json",
    };
    Object.assign(targetOptions, options);
    return submit(typedAction, targetOptions);
  };
}
