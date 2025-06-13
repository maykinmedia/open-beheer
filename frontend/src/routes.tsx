import { Navigate, Outlet, RouteObject } from "react-router";
import App from "~/App.tsx";
import {
  CatalogiPage,
  LoginPage,
  ZaaktypePage,
  ZaaktypenPage,
  catalogiAction,
  catalogiLoader,
  loginAction,
  loginLoader,
  zaaktypeAction,
  zaaktypeLoader,
  zaaktypenAction,
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
        element: <Navigate to="/catalogus" replace />,
      },
      {
        id: "catalogus",
        path: "catalogus",
        element: <CatalogiPage />,
        loader: catalogiLoader,
        action: catalogiAction,
        children: [
          {
            id: "catalogus-selected",
            path: ":catalogusId",
            element: <Outlet />,
            children: [
              {
                id: "zaaktypen",
                path: "zaaktypen",
                element: <ZaaktypenPage />,
                loader: zaaktypenLoader,
                action: zaaktypenAction,
                children: [
                  {
                    id: "zaaktype",
                    path: ":zaaktypeId",
                    element: <ZaaktypePage />,
                    loader: zaaktypeLoader,
                    action: zaaktypeAction,
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
    ],
  },
];
