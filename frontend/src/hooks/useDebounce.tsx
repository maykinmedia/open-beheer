import { debounce } from "@maykin-ui/client-common";
import { useState } from "react";

/**
 * Creates a debounced version of the provided function.
 * The function invocation will be delayed by the given `timeout` in
 * milliseconds.
 * Subsequent calls reset the timeout timer.
 *
 * @param fn - The function to debounce.
 * @param timeout - Delay in milliseconds before invoking `fn`. Defaults to 300.
 * @returns A debounced function with a `cancel` method.
 */
export function useDebounce<T extends (...args: Parameters<T>) => void>(
  fn: T,
  timeout?: number,
) {
  const [debouncedFn] = useState(() => debounce(fn, timeout));
  return debouncedFn;
}
