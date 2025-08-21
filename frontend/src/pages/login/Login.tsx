import { LoginTemplate, forceArray } from "@maykin-ui/admin-ui";
import { useActionData, useLoaderData, useSubmit } from "react-router";

type LoginFormType = { username: string; password: string };

/*
 * Add the redirect URL to the callback URL
 */
const makeRedirectUrl = (oidcLoginUrl: string) => {
  const currentUrl = new URL(window.location.href);
  const redirectUrl = new URL("/", currentUrl);
  const loginUrl = new URL(oidcLoginUrl);
  loginUrl.searchParams.set("next", redirectUrl.href);
  return loginUrl.href;
};

/**
 * Login page
 */
export function LoginPage() {
  const { oidcInfo } = useLoaderData();
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
      labelOidcLogin="Organisatie login"
      urlOidcLogin={
        oidcInfo.enabled ? makeRedirectUrl(oidcInfo.loginUrl) : undefined
      }
    />
  );
}
