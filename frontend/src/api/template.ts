import { request } from "~/api/request.ts";
import { ExpandItemKeys, RelatedObject } from "~/types";

export async function getRelatedObjectTemplateChoices<T extends object>(
  key: ExpandItemKeys<T>,
): Promise<RelatedObject<T>[]> {
  //localhost:8000/api/v1/service/{slug}/zaaktypen/{zaaktype}/besluittypen/
  return await request<RelatedObject<T>[]>("GET", `/template/${String(key)}/`);
}
