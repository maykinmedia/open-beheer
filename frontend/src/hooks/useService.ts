/**
 * Hook to manage the selected service in the application.
 * This hook provides functionality to get the current service and update it.
 */
import { useEffect, useState } from "react";
import { ServiceChoice, getServiceChoices } from "~/api/service.ts";

export function useService() {
  const [service, setService] = useState<ServiceChoice | null>(null);
  const [services, setServices] = useState<ServiceChoice[]>([]);

  useEffect(() => {
    const controller = new AbortController();

    const fetchServices = async () => {
      try {
        const serviceChoices = await getServiceChoices();
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
  }, []);

  return { service, services, setService };
}
