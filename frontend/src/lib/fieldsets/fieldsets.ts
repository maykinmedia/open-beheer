import { FieldSet } from "@maykin-ui/admin-ui";
import { slugify } from "@maykin-ui/client-common";
import { AttributeGridTabConfig, DataGridTabConfig, TabConfig } from "~/pages";
import { components } from "~/types";

export function convertFieldsetsToTabConfig<T extends object>(
  fieldsets: [string, components["schemas"]["FrontendFieldSet"]][],
): () => TabConfig<T>[] {
  return () =>
    fieldsets
      .map((fieldset) => {
        const [label, { fields }] = fieldset;
        const key = label ? slugify(label) : null;

        // _expand fields imply DataGrid.
        const fieldsAreExpanded = fields.find((field) =>
          field.includes("_expand"),
        );
        const view = fieldsAreExpanded ? "DataGrid" : "AttributeGrid";

        if (view === "AttributeGrid") {
          return {
            key: key,
            label,
            view,
            sections: [{ label, fieldsets: [[label, { fields }]] }],
          } as AttributeGridTabConfig<T>;
        }

        return {
          key: key,
          fieldset: fieldset as unknown as FieldSet,
          label,
          view,
          sections: [{ label, key: key }],
        } as DataGridTabConfig<T>;
      })
      .filter((tabConfig): tabConfig is TabConfig<T> => Boolean(tabConfig));
}
