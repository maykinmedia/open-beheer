import {
  BaseTemplate,
  ButtonProps,
  ConfigContext,
  Logo,
  Outline,
  ucFirst,
} from "@maykin-ui/admin-ui";
// @ts-expect-error - no ts modules
import "@maykin-ui/admin-ui/style";
import { useMemo } from "react";
import { Outlet, RouteObject, useLocation, useNavigate } from "react-router";
import { useChildRoutes } from "~/api/hooks/useChildRoutes.ts";
import { useCurrentMatch } from "~/api/hooks/useCurrentMatch.ts";
import { ROUTE_IDS } from "~/routes.tsx";

import "./main.css";

/**
 * This component serves as the entry point for the React app and renders the main UI structure.
 */
function App() {
  const location = useLocation();
  const navigate = useNavigate();
  const currentMatch = useCurrentMatch();
  const routeId = currentMatch?.id;
  const childRoutes = useChildRoutes();

  /**
   * The primary navigation items.
   */
  const primaryNavigationItems = useMemo(() => {
    // Login page should not show primary navigation.
    if (routeId === ROUTE_IDS.LOGIN) {
      return [];
    }

    const buttons = [
      {
        children: (
          <>
            <Outline.Squares2X2Icon />
          </>
        ),
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
    ];
  }, [location, routeId]);

  /**
   * The sidebar navigation items.
   */
  const sidebarItems = useMemo(() => {
    // Login page should not show sidebar.
    // Page with no child routes should not show sidebar.
    if (routeId === ROUTE_IDS.LOGIN || !childRoutes.length) {
      return [];
    }

    return childRoutes
      .filter((route) => route.path)
      .map(
        ({ path }: RouteObject): ButtonProps => ({
          onClick: () => navigate([currentMatch?.pathname, path!].join("/")),
          children: ucFirst(path?.split("/").pop()?.trim() || ""),
          align: "start",
        }),
      );
  }, [primaryNavigationItems]);

  return (
    <BaseTemplate
      primaryNavigationItems={primaryNavigationItems}
      sidebarItems={sidebarItems}
    >
      <ConfigContext.Provider value={{ templatesContentOnly: true }}>
        <Outlet />
      </ConfigContext.Provider>
    </BaseTemplate>
  );
}

export default App;
