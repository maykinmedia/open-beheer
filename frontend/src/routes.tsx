import { Navigate, Outlet, RouteObject } from "react-router";
import App, { CATALOGUS_PARAM, SERVICE_PARAM, SIDEBAR_INDEX } from "~/App.tsx";
import {
  LoginPage,
  ZaaktypePage,
  ZaaktypenPage,
  loginAction,
  loginLoader,
  logoutLoader,
  serviceLoader,
  zaaktypeLoader,
  zaaktypenLoader,
} from "~/pages";

/**
 * Available routes.
 */
export const routes: RouteObject[] = [
  {
    id: "root",
    path: "/",
    element: <App />,
    children: [
      {
        index: true,
        loader: serviceLoader,
      },
      {
        id: "service",
        path: `:${SERVICE_PARAM}`,
        element: <Outlet />,
        children: [
          {
            id: SIDEBAR_INDEX,
            path: `:${CATALOGUS_PARAM}`,
            element: <Outlet />,
            children: [
              {
                index: true,
                element: <Navigate to="zaaktypen" replace={true} />,
              },
              {
                id: "zaaktypen",
                path: "zaaktypen",
                element: <ZaaktypenPage />,
                loader: zaaktypenLoader,
                children: [
                  {
                    id: "zaaktype",
                    path: ":zaaktypeUUID",
                    element: <ZaaktypePage />,
                    loader: zaaktypeLoader,
                    shouldRevalidate: ({ currentUrl, nextUrl }) => {
                      const baseCurrent =
                        currentUrl.origin +
                        currentUrl.pathname +
                        currentUrl.search;
                      const baseNext =
                        nextUrl.origin + nextUrl.pathname + nextUrl.search;

                      // If base is the same but hash differs, do NOT revalidate
                      if (
                        baseCurrent === baseNext &&
                        currentUrl.hash !== nextUrl.hash
                      ) {
                        return false;
                      }

                      // Otherwise, revalidate
                      return true;
                    },
                  },
                ],
              },
            ],
          },
        ],
      },
      {
        id: "login",
        path: "/login",
        element: <LoginPage />,
        loader: loginLoader,
        action: loginAction,
        handle: {
          hideUi: true,
        },
      },
      {
        id: "logout",
        path: "/logout",
        element: <Navigate to="/login" />,
        loader: logoutLoader,
        handle: {
          hideUi: true,
        },
      },
    ],
  },
];
