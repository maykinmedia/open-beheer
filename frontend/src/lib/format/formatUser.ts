import { components } from "~/types";

export function formatUser(
  user: components["schemas"]["User"],
  { showUsername = true } = {},
) {
  let displayName = "";
  if (!user) return displayName;

  if (!user.firstName && !user.lastName) return user.username;

  if (user.firstName)
    displayName = displayName.concat(user.firstName.trim(), " ");
  if (user.lastName)
    displayName = displayName.concat(user.lastName.trim(), " ");
  if (showUsername)
    displayName = displayName.concat(`(${user.username.trim()})`);

  return displayName.trim();
}
