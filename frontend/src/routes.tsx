import { Navigate, RouteObject } from "react-router";
import App from "~/App.tsx";
import {
  CatalogiPage,
  LoginPage,
  ZaaktypenPage,
  catalogiAction,
  catalogiLoader,
  loginAction,
  loginLoader,
  zaaktypenAction,
  zaaktypenLoader,
} from "~/pages";

/**
 * Route id's used to identify a specific route.
 */
export const ROUTE_IDS = {
  LOGIN: "login",
  CATALOGI: "catalogi",
};

export type ROUTE_IDS = typeof ROUTE_IDS;
export type VALID_ROUTE_ID = ROUTE_IDS[keyof ROUTE_IDS];

/**
 * Available routes.
 */
export const routes: RouteObject[] = [
  {
    path: "/",
    element: <App />,
    children: [
      {
        path: "/",
        element: <Navigate to="/catalogi" replace />,
      },
      {
        id: ROUTE_IDS.CATALOGI,
        path: "/catalogi",
        element: <CatalogiPage />,
        loader: catalogiLoader,
        action: catalogiAction,
        children: [
          {
            path: "zaaktypen",
            element: <ZaaktypenPage />,
            loader: zaaktypenLoader,
            action: zaaktypenAction,
          },
        ],
      },
      {
        id: ROUTE_IDS.LOGIN,
        path: "/login",
        element: <LoginPage />,
        loader: loginLoader,
        action: loginAction,
      },
    ],
  },
];
