// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-expect-error
import "@maykin-ui/admin-ui/style";
import { Outlet } from "react-router";

/**
 * Root component of the application.
 *
 * This component serves as the entry point for the React app and renders the main UI structure.
 */
function App() {
  return (
    <>
      <Outlet />
    </>
  );
}

export default App;
