import { Errors, useAlert } from "@maykin-ui/admin-ui";
import { cacheGet, cacheSet } from "@maykin-ui/client-common";
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router";
import { getCatalogiChoices } from "~/api/catalogi.ts";
import { getUUIDFromString } from "~/lib/format/string.ts";
import { components } from "~/types";

/**
 * Hook to manage the catalogi choices and selected catalogi in the application.
 */
export function useCatalogi(
  service: components["schemas"]["OBOption_str_"] | null,
) {
  const navigate = useNavigate();
  const params = useParams();
  const selectedCatalogusId = params.catalogusId;
  const cacheKey = `selectedCatalogusId:${service?.value ?? "unknown"}`;

  const [catalogiChoices, setCatalogiChoices] = useState<
    components["schemas"]["OBOption_str_"][]
  >([]);
  const alert = useAlert();

  const handleCatalogusChange = (newCatalogusId: string) => {
    if (newCatalogusId) {
      void cacheSet(cacheKey, newCatalogusId);
      navigate(`/${service?.value}/${getUUIDFromString(newCatalogusId)}`);
    } else {
      navigate(`/${service?.value}`);
    }
  };

  useEffect(() => {
    const controller = new AbortController();

    const fetchCatalogiChoices = async () => {
      if (!service) {
        setCatalogiChoices([]);
        return;
      }

      try {
        const choices = await getCatalogiChoices(service.value);
        setCatalogiChoices(choices);

        // Auto-navigate logic
        if (!selectedCatalogusId) {
          const cachedId = await cacheGet<string>(cacheKey);

          if (cachedId && choices.some((c) => c.value === cachedId)) {
            handleCatalogusChange(cachedId);
            return;
          }

          if (choices.length === 1) {
            handleCatalogusChange(choices[0].value);
            return;
          }
        }
      } catch (error) {
        const messages: string[] = ["Failed to fetch catalogi choices."];
        if (error instanceof Response) {
          messages.push(`Status: ${error.status}, ${error.statusText}`);
        }
        alert(
          "Foutmelding",
          (<Errors errors={messages} />) as unknown as string, // TODO: Fix in admin-ui
          "Ok",
        );
      }
    };

    void fetchCatalogiChoices();

    return () => {
      controller.abort();
    };
  }, [service]);

  return {
    catalogiChoices,
    handleCatalogusChange,
    selectedCatalogusId,
  };
}
