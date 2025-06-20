import {
  SetURLSearchParams,
  URLSearchParamsInit,
  useSearchParams,
} from "react-router";
import { useDebounce } from "~/hooks/useDebounce.tsx";

/**
 * Wraps `useSearchParams()`, combines instead of replaces current URLSearchParams.
 * @param debounceTimeout - Optional, overrides the timeout on debounced
 *  setCombinedSearchParams.
 */
export function useCombinedSearchParams(
  debounceTimeout?: number,
): ReturnType<typeof useSearchParams> {
  const [searchParams, setSearchParams] = useSearchParams();
  const setCombinedSearchParams = useDebounce(handle, debounceTimeout);

  /**
   * Updates combined `searchParams`.
   * @param params - Query params to add.
   */
  function handle(params: URLSearchParamsInit) {
    const combinedParams = {
      ...Object.fromEntries(searchParams),
      ...(params as Record<string, string>),
    };

    const activeParams = Object.fromEntries(
      Object.entries(combinedParams).filter((keyValuePair) => keyValuePair[1]),
    );
    setSearchParams(new URLSearchParams(activeParams));
  }

  return [searchParams, setCombinedSearchParams as SetURLSearchParams];
}
