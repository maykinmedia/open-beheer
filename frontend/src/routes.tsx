import {
  Navigate,
  Outlet,
  RouteObject,
  isRouteErrorResponse,
  useRouteError,
} from "react-router";
import App, { CATALOGUS_PARAM, SERVICE_PARAM, SIDEBAR_INDEX } from "~/App.tsx";
import {
  LoginPage,
  ZaaktypeCreatePage,
  ZaaktypePage,
  ZaaktypenPage,
  cleanUp,
  loginAction,
  loginLoader,
  logoutLoader,
  serviceLoader,
  zaaktypeCreateAction,
  zaaktypeCreateLoader,
  zaaktypeLoader,
  zaaktypenLoader,
} from "~/pages";
import { InformatieObjectTypeCreatePage } from "~/pages/informatieobjecttypecreate/InformatieObjectTypeCreatePage";
import { InformatieObjectTypenPage } from "~/pages/informatieobjecttypen";
import { informatieobjecttypenLoader } from "~/pages/informatieobjecttypen/informatieobjecttype.loader";
import { zaaktypeAction } from "~/pages/zaaktype/zaaktype.action.ts";

import {
  InformatieObjectTypePage,
  informatieobjecttypeLoader,
} from "./pages/informatieobjecttype";
import { informatieobjecttypeAction } from "./pages/informatieobjecttype/informatieobjecttype.action";
import { informatieobjecttypeCreateAction } from "./pages/informatieobjecttypecreate/informatieobjecttype.action";

export function ErrorBoundary() {
  const error = useRouteError();

  if (isRouteErrorResponse(error) && error.status === 403) {
    if (error.data?.detail === "Authenticatiegegevens zijn niet opgegeven.") {
      cleanUp();
      // Redirect user to login as the session probably expired.
      const url = new URL(window.location.toString());
      return <Navigate to={`/login?next=${url.pathname}`} />;
    }
  }

  // TODO: Better errors for other cases
  return (
    <p>
      {error instanceof Error
        ? error.message
        : `Error: ${JSON.stringify(error)}`}
    </p>
  );
}

/**
 * Available routes.
 */
export const routes: RouteObject[] = [
  {
    id: "root",
    path: "/",
    element: <App />,
    errorElement: <ErrorBoundary />,
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
                element: <Outlet />,
                children: [
                  {
                    index: true,
                    element: <ZaaktypenPage />,
                    loader: zaaktypenLoader,
                  },
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
                element: <Outlet />,
                children: [
                  {
                    index: true,
                    element: <InformatieObjectTypenPage />,
                    loader: informatieobjecttypenLoader,
                  },
                  {
                    id: "create-informatieobjecttype",
                    path: "create",
                    element: <InformatieObjectTypeCreatePage />,
                    action: informatieobjecttypeCreateAction,
                  },
                  {
                    id: "informatieobjecttype",
                    path: ":informatieobjecttypeUUID",
                    element: <InformatieObjectTypePage />,
                    action: informatieobjecttypeAction,
                    loader: informatieobjecttypeLoader,
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
