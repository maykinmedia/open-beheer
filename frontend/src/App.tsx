import {
  BaseTemplate,
  ButtonProps,
  ConfigContext,
  H2,
  Hr,
  Logo,
  ModalService,
  Outline,
  Select,
} from "@maykin-ui/admin-ui";
// @ts-expect-error - no ts modules
import "@maykin-ui/admin-ui/style";
import { string2Title } from "@maykin-ui/client-common";
import { createContext, useEffect, useMemo, useState } from "react";
import {
  Outlet,
  RouteObject,
  useLocation,
  useMatches,
  useNavigate,
  useParams,
} from "react-router";
import { whoAmI } from "~/api";
import { Profile } from "~/components";
import {
  useCatalogi,
  useChildRoutes,
  useCurrentMatch,
  useService,
} from "~/hooks";
import { getUUIDFromString } from "~/lib/format/string.ts";
import { components } from "~/types";

import "./main.css";

/** Route id to show children for in the sidebar. */
export const SIDEBAR_INDEX = "catalogus";

/** Parameter name for the catalogus id in the URL. */
export const SERVICE_PARAM = "serviceSlug";

/** Parameter name for the catalogus id in the URL. */
export const CATALOGUS_PARAM = "catalogusId";

type OBContext = {
  catalogiChoices: components["schemas"]["list_OBOption_str_"];
};

export const OBContext = createContext<OBContext>({
  catalogiChoices: [],
});

/**
 * This component serves as the entry point for the React app and renders the main UI structure.
 */
function App() {
  const [user, setUser] = useState<components["schemas"]["User"] | null>(null);
  const location = useLocation();
  const navigate = useNavigate();
  const params = useParams();
  const matches = useMatches();
  const currentMatch = useCurrentMatch();
  const childRoutes = useChildRoutes(SIDEBAR_INDEX);
  const { service } = useService(user);
  const { catalogiChoices, handleCatalogusChange, selectedCatalogusId } =
    useCatalogi(service);

  const serviceSlug = params[SERVICE_PARAM];

  // Determine whether we should render the base UI.
  const currentMatchHandle = currentMatch.handle as
    | Record<string, unknown>
    | undefined;
  const hideUi = currentMatchHandle?.hideUi;

  useEffect(() => {
    if (hideUi) return;

    const controller = new AbortController();

    const fetchUser = async () => {
      try {
        const currentUser = await whoAmI(controller.signal);
        setUser(currentUser);
      } catch (error) {
        console.error("Failed to fetch user:", error);
      }
    };

    void fetchUser();

    return () => {
      controller.abort();
      setUser(null);
    };
  }, [hideUi]);

  /**
   * The primary navigation items.
   */
  const primaryNavigationItems = useMemo(() => {
    // Login page should not show primary navigation.
    if (hideUi) {
      return [];
    }

    const buttons = [
      {
        children: <Outline.Squares2X2Icon />,
        title: "Catalogi",
        onClick: () => navigate("/"),
      },
    ].map<ButtonProps>((props) => ({
      ...props,
      // eslint-disable-next-line react/prop-types
      key: props.title,
      align: "start",
      pad: true,
    }));
    return [
      <Logo key="logo" abbreviated variant="contrast" />,
      ...buttons,
      "spacer",
      <Profile key="Profile" user={user} />,
    ];
  }, [location, user]);

  /**
   * The sidebar navigation items.
   */
  const sidebarItems = useMemo(() => {
    // Page with no child routes should not show sidebar.
    if (hideUi || !childRoutes.length) {
      return [];
    }
    const items = childRoutes
      .filter((route) => route.path)
      .map(({ path, id }: RouteObject): ButtonProps => {
        return {
          active: Boolean(id && matches.map((m) => m.id).includes(id)),
          align: "start",
          children: string2Title(path?.split("/").pop()?.trim() || ""),
          disabled: !selectedCatalogusId,
          onClick: () => {
            navigate(`${serviceSlug}/${selectedCatalogusId}/${path}`);
          },
        };
      });
    return [
      <H2 key="product-name">Open Beheer</H2>,
      <Hr key="hr" margin="xs" />,
      <Select
        key="catalogi-select"
        disabled={catalogiChoices.length === 0}
        options={catalogiChoices.map((c) => ({
          label: c.label,
          value: getUUIDFromString(c.value) || "",
        }))}
        placeholder="Selecteer catalogus"
        value={selectedCatalogusId}
        variant="secondary"
        onChange={({ target }) => handleCatalogusChange(target.value)}
      />,
      ...items,
    ];
  }, [primaryNavigationItems, catalogiChoices]);

  return (
    <BaseTemplate
      primaryNavigationItems={primaryNavigationItems}
      sidebarItems={sidebarItems}
      grid={!hideUi}
    >
      <ModalService>
        <ConfigContext.Provider
          value={{ templatesContentOnly: true, templatesGrid: false }}
        >
          <OBContext.Provider value={{ catalogiChoices }}>
            <Outlet />
          </OBContext.Provider>
        </ConfigContext.Provider>
      </ModalService>
    </BaseTemplate>
  );
}

export default App;
