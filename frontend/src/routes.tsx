import { Navigate, RouteObject } from "react-router";
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
        id: "index",
        path: "/",
        element: <Navigate to="/catalogi" replace />,
      },
      {
        id: "catalogi",
        path: "catalogi",
        element: <CatalogiPage />,
        loader: catalogiLoader,
        action: catalogiAction,
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
                path: ":uuid",
                element: <ZaaktypePage />,
                loader: zaaktypeLoader,
                action: zaaktypeAction,
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
