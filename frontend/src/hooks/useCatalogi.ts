/**
 * Hook to manage the catalogi choices and selected catalogi in the application.
 */
import { useEffect, useState } from "react";
import { getCatalogiChoices } from "~/api/catalogi.ts";
import { components } from "~/types";

export function useCatalogi(
  service: components["schemas"]["OBOption_str_"] | null,
) {
  const [catalogiChoices, setCatalogiChoices] = useState<
    components["schemas"]["OBOption_str_"][]
  >([]);

  useEffect(() => {
    const controller = new AbortController();

    const fetchCatalogiChoices = async () => {
      if (service) {
        try {
          const choices = await getCatalogiChoices(service.value);
          setCatalogiChoices(choices);
        } catch (error) {
          console.error("Failed to fetch catalogi choices:", error);
        }
      } else {
        setCatalogiChoices([]);
      }
    };

    void fetchCatalogiChoices();

    return () => {
      controller.abort();
    };
  }, [service]);

  return {
    catalogiChoices,
  };
}
