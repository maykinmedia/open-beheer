/**
 * Hook to manage the catalogi choices and selected catalogi in the application.
 */
import { useEffect, useState } from "react";
import { CatalogiChoice, getCatalogiChoices } from "~/api/catalogi.ts";
import { ServiceChoice } from "~/api/service.ts";

export function useCatalogi(service: ServiceChoice | null) {
  const [catalogiChoices, setCatalogiChoices] = useState<CatalogiChoice[]>([]);

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
