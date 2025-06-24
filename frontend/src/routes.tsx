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
