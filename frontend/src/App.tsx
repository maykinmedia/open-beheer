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
import { useEffect, useMemo, useState } from "react";
import { Outlet, RouteObject, useLocation, useNavigate } from "react-router";
import { Profile } from "~/components/Profile/Profile.tsx";
import { User, whoAmI } from "~/lib";
import { useChildRoutes } from "~/lib/hooks/useChildRoutes.ts";
import { useCurrentMatch } from "~/lib/hooks/useCurrentMatch.ts";

import "./main.css";

/**
 * This component serves as the entry point for the React app and renders the main UI structure.
 */
function App() {
  const location = useLocation();
  const navigate = useNavigate();
  const currentMatch = useCurrentMatch();
  const childRoutes = useChildRoutes();
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
    if (!childRoutes.length) {
      return [];
    }

    return childRoutes
      .filter((route) => route.path)
      .map(({ path, id }: RouteObject): ButtonProps => {
        return {
          active: currentMatch.id === id,
          align: "start",
          children: ucFirst(path?.split("/").pop()?.trim() || ""),
          onClick: () =>
            navigate(
              currentMatch.id === id
                ? currentMatch.pathname || ""
                : [currentMatch.pathname, path!].join("/"),
            ),
        };
      });
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
