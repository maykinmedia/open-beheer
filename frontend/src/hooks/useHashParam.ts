import { useCallback, useEffect, useState } from "react";

/**
 * Custom hook to manage a hash parameter in the URL.
 * @param key - The key of the hash parameter to manage.
 * @param defaultValue - The default value if the parameter doesn't exist.
 */
export function useHashParam(key: string, defaultValue: string) {
  const getHashValue = useCallback(() => {
    const params = new URLSearchParams(window.location.hash.slice(1));
    return params.get(key) || defaultValue;
  }, [key, defaultValue]);

  const [value, setValue] = useState<string>(() => getHashValue());

  const updateHash = useCallback(
    (newValue: string) => {
      const params = new URLSearchParams(window.location.hash.slice(1));
      params.set(key, newValue);
      window.location.hash = params.toString();
      setValue(newValue);
    },
    [key],
  );

  useEffect(() => {
    const onHashChange = () => {
      setValue(getHashValue());
    };
    window.addEventListener("hashchange", onHashChange);
    return () => {
      window.removeEventListener("hashchange", onHashChange);
    };
  }, [getHashValue]);

  return [value, updateHash] as const;
}
