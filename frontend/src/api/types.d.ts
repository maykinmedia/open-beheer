import { FieldSet, PaginatorProps, TypedField } from "@maykin-ui/admin-ui";

export type ListResponse<T extends object = object> = {
  fields: TypedField<T>[];
  pagination: PaginatorProps;
  results: T[];
};

export type DetailResponse<T extends object = object> = {
  fields: TypedField<T>[];
  fieldsets: FieldSet<T>[];
  result: T;
};
