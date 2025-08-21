import { LoginTemplate } from "@maykin-ui/admin-ui";
import { forceArray } from "@maykin-ui/client-common";
import { useActionData, useSubmit } from "react-router";

type LoginFormType = { username: string; password: string };

/**
 * Login page
 */
export function LoginPage() {
  const actionData = useActionData() || {};
  const submit = useSubmit();

  const fields = [
    {
      autoFocus: true,
      autoComplete: "username",
      label: "Gebruikersnaam",
      name: "username",
      type: "text",
    },
    {
      autoComplete: "current-password",
      label: "Wachtwoord",
      name: "password",
      type: "password",
    },
  ];

  const formErrors = Object.fromEntries(
    Object.entries(actionData).map(([key, values]) => [
      key,
      forceArray(values)?.join(", "),
    ]),
  );
  const { detail, nonFieldErrors, ...errors } = formErrors;

  return (
    <LoginTemplate<LoginFormType>
      contentOnly={false} // Explicit to override context.
      slotPrimaryNavigation={<></>} // FIXME: Should be easier to override
      formProps={{
        "aria-label": "Vul uw inloggegevens in",
        nonFieldErrors: nonFieldErrors || detail,
        errors,
        fields,
        onSubmit: (_, data) => submit(data, { method: "POST" }),
      }}
    />
  );
}
