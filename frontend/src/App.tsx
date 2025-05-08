import {
  BaseTemplate,
  ButtonProps,
  ConfigContext,
  H2,
  Hr,
  Logo,
  Outline,
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
} from "react-router";
import { User, whoAmI } from "~/api";
import { Profile } from "~/components/Profile/Profile.tsx";
import { useChildRoutes, useCurrentMatch } from "~/hooks";

import "./main.css";

/** Route id to show children for in the sidebar. */
const SIDEBAR_INDEX = "catalogi";

/**
 * This component serves as the entry point for the React app and renders the main UI structure.
 */
function App() {
  const location = useLocation();
  const navigate = useNavigate();
  const matches = useMatches();
  const currentMatch = useCurrentMatch();
  const childRoutes = useChildRoutes(SIDEBAR_INDEX);
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
          onClick: () => {
            navigate("/catalogi/" + path);
          },
        };
      });
    return [
      <H2 key="product-name">Open Beheer</H2>,
      <Hr key="hr" size="xxl" />,
      ...items,
    ];
  }, [primaryNavigationItems]);

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
