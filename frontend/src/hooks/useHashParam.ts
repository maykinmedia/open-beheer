import { useCallback, useEffect, useState } from "react";

/**
 * Hook for managing a specific hash parameter in the URL.
 * Initializes with a default value if missing.
 *
 * @param key - Hash parameter key to manage.
 * @param defaultValue - Default value if the key is not present.
 * @returns A tuple of [current value, setValue function].
 */
export function useHashParam(
  key: string,
  defaultValue: string,
): [string | null, (value: string, replace?: boolean) => void] {
  const [hash, setHash] = useState<string>(); // Only for renders.

  /** Gets current hash params as URLSearchParams. */
  const _getParams = () => {
    const hash = window.location.hash.slice(1);
    return new URLSearchParams(hash);
  };

  /**
   * Updates the URL hash from given params.
   * @param params - Parameters to encode into the hash.
   * @param replace - If true, replaces current history entry.
   */
  const _setHashParams = useCallback(
    (params: URLSearchParams, replace: boolean) => {
      const url = new URL(window.location.href);
      const paramString = params.toString();
      const newHash = paramString ? `#${paramString}` : "";

      setHash(url.hash.slice(0));
      if (newHash == url.hash) return;

      url.hash = newHash;
      if (replace) {
        window.history.replaceState(null, "", url.toString());
      } else {
        window.history.pushState(null, "", url.toString());
      }
    },
    [hash, window.location.href],
  );

  /** Gets the current value of the specified hash key. */
  const getValue = useCallback(() => _getParams().get(key), [key]);

  /**
   * Sets the value for the specified hash key.
   * @param value - Value to set.
   * @param replace - If true, replaces current history entry.
   */
  const setValue = useCallback(
    (value: string, replace = false) => {
      const params = _getParams();
      params.set(key, value);
      _setHashParams(params, replace);
    },
    [_getParams, _setHashParams],
  );

  // Set the default value.
  useEffect(() => {
    const value = getValue();
    if (value === null) {
      setValue(defaultValue, true);
    }
  }, [key, getValue, setValue]);

  // Sync with external changes.
  useEffect(() => {
    const listener = () => {
      const params = _getParams();
      setHash(params.toString().slice(0));
    };
    window.addEventListener("popstate", listener);
    return () => window.removeEventListener("popstate", listener);
  }, []);

  const value = getValue();
  return [value, setValue];
}
