import {
  BaseTemplate,
  Button,
  ButtonProps,
  Card,
  ConfigContext,
  H2,
  Hr,
  Outline,
  P,
  Select,
  Solid,
  useDialog,
} from "@maykin-ui/admin-ui";
import "@maykin-ui/admin-ui/style";
import { string2Title } from "@maykin-ui/client-common";
import {
  Fragment,
  MouseEventHandler,
  createContext,
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";
import {
  Outlet,
  RouteObject,
  useLocation,
  useMatches,
  useNavigate,
  useNavigation,
  useParams,
} from "react-router";
import { API_URL, whoAmI } from "~/api";
import { Profile } from "~/components";
import {
  useCatalogi,
  useChildRoutes,
  useCurrentMatch,
  useService,
} from "~/hooks";
import { getUUIDFromString } from "~/lib/format/string.ts";
import { components } from "~/types";

import "./main.css";

/** Route id to show children for in the sidebar. */
export const SIDEBAR_INDEX = "catalogus";

/** Parameter name for the catalogus id in the URL. */
export const SERVICE_PARAM = "serviceSlug";

/** Parameter name for the catalogus id in the URL. */
export const CATALOGUS_PARAM = "catalogusId";

type OBContext = {
  catalogiChoices: components["schemas"]["list_OBOption_str_"];
};

export const OBContext = createContext<OBContext>({
  catalogiChoices: [],
});

/** The base origin for all API requests. */
export const STATIC_URL =
  import.meta.env.MYKN_STATIC_URL || API_URL + "/static";

/**
 * This component serves as the entry point for the React app and renders the main UI structure.
 */
function App() {
  const [user, setUser] = useState<components["schemas"]["User"] | null>(null);
  const location = useLocation();
  const navigate = useNavigate();
  const { state } = useNavigation();
  const params = useParams();
  const matches = useMatches();
  const currentMatch = useCurrentMatch();
  const childRoutes = useChildRoutes(SIDEBAR_INDEX);
  const { service } = useService(user);
  const { catalogiChoices, handleCatalogusChange, selectedCatalogusId } =
    useCatalogi(service);

  const serviceSlug = params[SERVICE_PARAM];

  // Determine whether we should render the base UI.
  const currentMatchHandle = currentMatch.handle as
    | Record<string, unknown>
    | undefined;
  const hideUi = currentMatchHandle?.hideUi;

  useEffect(() => {
    if (hideUi) return;

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
  }, [hideUi]);

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
      <Logo key="logo" about abbreviated />,
      ...buttons,
      "spacer",
      <Fragment key="spinner">
        {state !== "idle" ? (
          <P title="Bezig met laden...">
            <Solid.ArrowPathIcon
              spin
              stroke="var(--button-color-text-primary)"
            />
          </P>
        ) : undefined}
      </Fragment>,
      <Profile key="Profile" user={user} />,
    ];
  }, [location, state, user]);

  /**
   * The sidebar navigation items.
   */
  const sidebarItems = useMemo(() => {
    // Page with no child routes should not show sidebar.
    if (hideUi || !childRoutes.length) {
      return [];
    }
    const items = childRoutes
      .filter((route) => route.path)
      .map(({ path, id }: RouteObject): ButtonProps => {
        return {
          active: Boolean(id && matches.map((m) => m.id).includes(id)),
          align: "start",
          children: string2Title(path?.split("/").pop()?.trim() || ""),
          disabled: !selectedCatalogusId,
          onClick: () => {
            navigate(`${serviceSlug}/${selectedCatalogusId}/${path}`);
          },
        };
      });
    return [
      <H2 key="product-name">Open Beheer</H2>,
      <Hr key="hr" margin="xs" />,
      <Select
        key="catalogi-select"
        disabled={catalogiChoices.length === 0}
        options={catalogiChoices.map((c) => ({
          label: c.label,
          value: getUUIDFromString(c.value) || "",
        }))}
        placeholder="Selecteer catalogus"
        value={selectedCatalogusId}
        variant="secondary"
        onChange={({ target }) => handleCatalogusChange(target.value)}
      />,
      ...items,
    ];
  }, [primaryNavigationItems, catalogiChoices]);

  return (
    <BaseTemplate
      primaryNavigationItems={primaryNavigationItems}
      sidebarItems={sidebarItems}
      grid={!hideUi}
    >
      <ConfigContext.Provider
        value={{
          logo: <Logo />,
          templatesContentOnly: true,
          templatesGrid: false,
        }}
      >
        <OBContext.Provider value={{ catalogiChoices }}>
          <Outlet />
        </OBContext.Provider>
      </ConfigContext.Provider>
    </BaseTemplate>
  );
}

type LogoProps = {
  /** Whether to show the about box on click. */
  about?: boolean;

  /** Whether to use the short "abbreviated" icon instead of the logo. */
  abbreviated?: boolean;
};

function Logo({ about, abbreviated }: LogoProps) {
  const dialog = useDialog();

  const handleCLick = useCallback<MouseEventHandler<HTMLButtonElement>>(
    () =>
      dialog(
        "Over",
        <Card>
          <img
            className="ob-logo"
            alt="Open Beheer logo"
            src={`${STATIC_URL}/ico/open-beheer-logo.svg`}
          />
        </Card>,
        undefined,
        { size: "m" },
      ),
    [],
  );

  const image = (
    <img
      className="ob-logo"
      alt="Open Beheer logo"
      src={`${STATIC_URL}/ico/open-beheer-${abbreviated ? "icon" : "logo"}.svg`}
    />
  );

  return about ? (
    <Button
      size={abbreviated ? "xs" : undefined}
      square={abbreviated}
      variant="transparent"
      onClick={handleCLick}
    >
      {image}
    </Button>
  ) : (
    image
  );
}

export default App;
