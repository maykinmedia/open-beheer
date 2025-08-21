import { request } from "~/api/request.ts";
import { ExpandItemKeys, RelatedObject } from "~/types";

export async function getRelatedObjectTemplateChoices<T extends object>(
  key: ExpandItemKeys<T>,
): Promise<RelatedObject<T>[]> {
  return await request<RelatedObject<T>[]>("GET", `/template/${String(key)}/`);
}
