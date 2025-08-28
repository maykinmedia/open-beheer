import { components } from "~/types";

export function formatUser(
  user: components["schemas"]["User"],
  { showUsername = true } = {},
) {
  let displayName = "";
  if (!user) return displayName;

  // eslint-disable-next-line @typescript-eslint/ban-ts-comment
  // @ts-expect-error
  if (!user.firstName && !user.lastName) return user.username;

  // eslint-disable-next-line @typescript-eslint/ban-ts-comment
  // @ts-expect-error
  if (user.firstName)
    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-expect-error
    displayName = displayName.concat(user.firstName.trim(), " ");
  // eslint-disable-next-line @typescript-eslint/ban-ts-comment
  // @ts-expect-error
  if (user.lastName)
    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-expect-error
    displayName = displayName.concat(user.lastName.trim(), " ");
  if (showUsername)
    displayName = displayName.concat(`(${user.username.trim()})`);

  return displayName.trim();
}
