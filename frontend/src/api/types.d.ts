import { PaginatorProps, TypedField } from "@maykin-ui/admin-ui";

export type ListResponse<T extends object = object> = {
  fields: TypedField<T>[];
  pagination: PaginatorProps;
  results: T[];
};

export type OidcInfoType = {
  enabled: boolean;
  loginUrl?: string;
};
