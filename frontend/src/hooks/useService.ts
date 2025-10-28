/**
 * Hook to manage the selected service in the application.
 * This hook provides functionality to get the current service and update it.
 */
import { invariant } from "@maykin-ui/client-common/assert";
import { useEffect, useState } from "react";
import { getServiceChoices } from "~/api/service.ts";
import { components } from "~/types";

/**
 * Returns the first available service.
 * @param user - Only fetch if truthy.
 */
export function useService(user: components["schemas"]["User"] | null) {
  const [service, setService] = useState<
    components["schemas"]["OBOption_str_"] | null
  >(null);
  const [services, setServices] = useState<
    components["schemas"]["OBOption_str_"][]
  >([]);

  useEffect(() => {
    if (!user) return;

    const controller = new AbortController();

    const fetchServices = async () => {
      try {
        const serviceChoices = await getServiceChoices();
        invariant(
          serviceChoices,
          "The service choices are unexpectedly undefined.",
        );
        setServices(serviceChoices);
        setService(serviceChoices[0] ?? null);
      } catch (error) {
        console.error("Failed to fetch services:", error);
      }
    };

    void fetchServices();

    return () => {
      controller.abort();
    };
  }, [user]);

  return { service, services, setService };
}
