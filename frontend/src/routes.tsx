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
 * Available routes.
 */
export const routes: RouteObject[] = [
  {
    path: "/",
    element: <App />,
    children: [
      {
        id: "root",
        path: "/",
        element: <Navigate to="/catalogi" replace />,
      },
      {
        id: "catalogi",
        path: "/catalogi",
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
