import { useActionData } from "react-router";
import { invalidParams2Errors } from "~/lib";

/**
 * Custom hook returning errors object based on action response.
 */
export function useErrors() {
  const errors = useActionData() || {};
  return invalidParams2Errors(errors?.invalidParams);
}
