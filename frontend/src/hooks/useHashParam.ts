import { invariant } from "@maykin-ui/client-common/assert";
import { useCallback, useEffect, useRef, useState } from "react";

/**
 * Custom hook to manage a hash parameter in the URL.
 * @param key - The key of the hash parameter to manage.
 * @param defaultValue - The default value if the parameter doesn't exist.
 */
export function useHashParam(
  key: string,
  defaultValue: string,
): [string, (newValue: string) => void] {
  const initialKeyRef = useRef(key);

  invariant(
    key === initialKeyRef.current,
    "The key for useHashParam should never change",
  );

  const getHashValue = useCallback(() => {
    const params = new URLSearchParams(window.location.hash.slice(1));
    return params.get(key) || defaultValue;
  }, [key, defaultValue]);

  const [value, setValue] = useState<string>();

  // Sync value when defaultValue changes (if param not set)
  useEffect(() => {
    const params = new URLSearchParams(window.location.hash.slice(1));
    if (!params.has(key)) {
      setValue(defaultValue);
    }
  }, [defaultValue, key]);

  /**
   * Updates the hash value.
   * @param newValue - Value to replace hash with.
   * @param replace - If true, use history.replaceState instead of setting window.location.hash
   */
  const updateHash = useCallback(
    (newValue: string, replace: boolean = false) => {
      const params = new URLSearchParams(window.location.hash.slice(1));
      params.set(key, newValue);
      const newHash = params.toString();

      if (replace) {
        const url = new URL(window.location.href);
        url.hash = newHash ? `#${newHash}` : "";
        window.history.replaceState(null, "", url.toString());
      } else {
        window.location.hash = newHash;
      }

      setValue(newValue);
    },
    [key],
  );

  useEffect(() => {
    if (typeof value === "undefined") {
      updateHash(defaultValue, true);
    }

    const onHashChange = () => {
      setValue(getHashValue());
    };
    window.addEventListener("hashchange", onHashChange);
    return () => {
      window.removeEventListener("hashchange", onHashChange);
    };
  }, [getHashValue]);

  return [
    typeof value === "undefined" ? defaultValue : value,
    updateHash,
  ] as const;
}
