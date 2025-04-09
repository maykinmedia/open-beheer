// @ts-expect-error Style is an alias, and ts isn't able to resolve this
import "@maykin-ui/admin-ui/style";
import { Outlet } from "react-router";

/**
 * This component serves as the entry point for the React app and renders the main UI structure.
 */
function App() {
  return <Outlet />;
}

export default App;
