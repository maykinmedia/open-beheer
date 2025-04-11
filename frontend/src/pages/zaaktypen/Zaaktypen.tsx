import { ListTemplate } from "@maykin-ui/admin-ui";
import { useLoaderData } from "react-router";

import "./Zaaktypen.css";

/**
 * Zaaktypen page
 */
export function ZaaktypenPage() {
  const { demoData } = useLoaderData();
  return (
    <ListTemplate
      dataGridProps={{
        title: "Zaaktypen",
        height: "fill-available-space",
        objectList: demoData,
      }}
    />
  );
}
