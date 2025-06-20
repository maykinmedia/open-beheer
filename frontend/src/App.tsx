import {
  BaseTemplate,
  ButtonProps,
  ConfigContext,
  H2,
  Hr,
  Logo,
  Outline,
  Select,
  ucFirst,
} from "@maykin-ui/admin-ui";
// @ts-expect-error - no ts modules
import "@maykin-ui/admin-ui/style";
import { useEffect, useMemo, useState } from "react";
import {
  Outlet,
  RouteObject,
  useLocation,
  useMatches,
  useNavigate,
  useParams,
} from "react-router";
import { User, whoAmI } from "~/api";
import { Profile } from "~/components";
import {
  useCatalogi,
  useChildRoutes,
  useCurrentMatch,
  useService,
} from "~/hooks";

import "./main.css";

/** Route id to show children for in the sidebar. */
export const SIDEBAR_INDEX = "catalogus";

/** Parameter name for the catalogus id in the URL. */
export const SERVICE_PARAM = "serviceSlug";

/** Parameter name for the catalogus id in the URL. */
export const CATALOGUS_PARAM = "catalogusId";

/**
 * This component serves as the entry point for the React app and renders the main UI structure.
 */
function App() {
  const location = useLocation();
  const navigate = useNavigate();
  const params = useParams();
  const matches = useMatches();
  const currentMatch = useCurrentMatch();
  const childRoutes = useChildRoutes(SIDEBAR_INDEX);
  const { service } = useService();
  const { catalogiChoices } = useCatalogi(service);

  const serviceSlug = params[SERVICE_PARAM];
  const catalogusId = params[CATALOGUS_PARAM];

  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
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
  }, []);

  // Determine whether we should render the base UI.
  const currentMatchHandle = currentMatch.handle as
    | Record<string, unknown>
    | undefined;
  const hideUi = currentMatchHandle?.hideUi;

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
          children: ucFirst(path?.split("/").pop()?.trim() || ""),
          disabled: !catalogusId,
          onClick: () => {
            navigate(`${serviceSlug}/${catalogusId}/${path}`);
          },
        };
      });
    return [
      <H2 key="product-name">Open Beheer</H2>,
      <Hr key="hr" size="xxl" />,
      <Select
        key="catalogi-select"
        disabled={catalogiChoices.length === 0}
        options={catalogiChoices}
        placeholder="Selecteer catalogus"
        value={catalogusId}
        variant="accent"
        onChange={({ target }) => {
          const { value } = target;

          if (!value) {
            navigate("/");
          }

          navigate(serviceSlug + "/" + value);
        }}
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
      <ConfigContext.Provider
        value={{ templatesContentOnly: true, templatesGrid: false }}
      >
        <Outlet />
      </ConfigContext.Provider>
    </BaseTemplate>
  );
}

export default App;
