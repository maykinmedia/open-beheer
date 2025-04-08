import { LoginTemplate, forceArray } from "@maykin-ui/admin-ui";
import React from "react";
import { useActionData, useSubmit } from "react-router";

import "./Login.css";

type LoginFormType = { username: string; password: string };

export type LoginPageProps = React.ComponentProps<"main"> & {
  // Props here.
};

/**
 * Login page
 */
export function LoginPage({ ...props }: LoginPageProps) {
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
      slotPrimaryNavigation={<></>} // FIXME: Should be easier to override
      formProps={{
        "aria-label": "Vul uw inloggegevens in",
        nonFieldErrors: nonFieldErrors || detail,
        errors,
        fields,
        onSubmit: (_, data) => submit(data, { method: "POST" }),
      }}
      {...props}
    />
  );
}
