import { components } from "~/types";

export function formatUser(
  user: components["schemas"]["User"],
  { showUsername = true } = {},
) {
  let displayName = "";
  if (!user) return displayName;

  if (!user.first_name && !user.last_name) return user.username;

  if (user.first_name)
    displayName = displayName.concat(user.first_name.trim(), " ");
  if (user.last_name)
    displayName = displayName.concat(user.last_name.trim(), " ");
  if (showUsername)
    displayName = displayName.concat(`(${user.username.trim()})`);

  return displayName.trim();
}
