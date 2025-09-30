import { Navigate, Outlet, RouteObject } from "react-router";
import App, { CATALOGUS_PARAM, SERVICE_PARAM, SIDEBAR_INDEX } from "~/App.tsx";
import {
  LoginPage,
  ZaaktypeCreatePage,
  ZaaktypePage,
  ZaaktypenPage,
  loginAction,
  loginLoader,
  logoutLoader,
  serviceLoader,
  zaaktypeCreateAction,
  zaaktypeCreateLoader,
  zaaktypeLoader,
  zaaktypenLoader,
} from "~/pages";
import { zaaktypeAction } from "~/pages/zaaktype/zaaktype.action.ts";
import { informatieobjecttypenLoader } from "./pages/informatieobjecttypen/informatieobjecttype.loader";
import { InformatieObjectTypenPage } from "./pages/informatieobjecttypen";

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
                    id: "create-zaaktype",
                    path: "create",
                    element: <ZaaktypeCreatePage />,
                    loader: zaaktypeCreateLoader,
                    action: zaaktypeCreateAction,
                  },
                  {
                    id: "zaaktype",
                    path: ":zaaktypeUUID",
                    element: <ZaaktypePage />,
                    action: zaaktypeAction,
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
              {
                id: "informatieobjecttypen",
                path: "informatieobjecttypen",
                element: <InformatieObjectTypenPage />,
                loader: informatieobjecttypenLoader,
                children: [],
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
