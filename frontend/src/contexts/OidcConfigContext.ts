import { createContext } from "react";

export type OidcConfigContextType = {
  enabled: boolean;
  loginUrl: string;
};

export const OidcConfigContext = createContext<OidcConfigContextType>({
  enabled: false,
  loginUrl: "",
});
