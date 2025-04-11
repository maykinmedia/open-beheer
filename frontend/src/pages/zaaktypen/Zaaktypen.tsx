import { ListTemplate, Modal } from "@maykin-ui/admin-ui";
import {
  useLoaderData,
  useLocation,
  useNavigate,
  useOutlet,
} from "react-router";
import { useRoutesPath } from "~/hooks";
import { ZaaktypenLoaderData } from "~/pages";

import "./Zaaktypen.css";

/**
 * Zaaktypen page
 */
export function ZaaktypenPage() {
  const { pathname } = useLocation();
  const { demoData } = useLoaderData<ZaaktypenLoaderData>();
  const navigate = useNavigate();
  const outlet = useOutlet();

  const routePath = useRoutesPath("zaaktypen");
  const zaakTypenPath =
    routePath
      ?.map((route) => route.path)
      .join("/")
      .replace(/\/+/, "/") || "";

  return (
    <ListTemplate
      dataGridProps={{
        title: "Zaaktypen",
        height: "fill-available-space",
        objectList: demoData.map((row) => ({
          ...row,
          href: `${pathname}/${row.id}`,
        })),
      }}
    >
      {outlet && (
        <Modal
          position="side"
          size="m"
          open={Boolean(outlet)}
          onClose={() => navigate(zaakTypenPath)}
        >
          {/*// @ts-expect-error - ?*/}
          {outlet}
        </Modal>
      )}
    </ListTemplate>
  );
}
