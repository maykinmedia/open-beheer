/**
 * Hook to manage the selected service in the application.
 * This hook provides functionality to get the current service and update it.
 */
import { useEffect, useState } from "react";
import { User } from "~/api";
import { ServiceChoice, getServiceChoices } from "~/api/service.ts";

/**
 * Returns the first available service.
 * @param user - Only fetch if truthy.
 */
export function useService(user: User | null) {
  const [service, setService] = useState<ServiceChoice | null>(null);
  const [services, setServices] = useState<ServiceChoice[]>([]);

  useEffect(() => {
    if (!user) return;

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
  }, [user]);

  return { service, services, setService };
}
