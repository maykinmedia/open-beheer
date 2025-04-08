import React from "react";
import { useLoaderData } from "react-router";

import "./Home.css";
import { HomeLoaderData } from "./Home.loader.tsx";

export type HomePageProps = React.ComponentProps<"main"> & {
  // Props here.
};

/**
 * Home page
 */
export function HomePage({ children, ...props }: HomePageProps) {
  const loaderData = useLoaderData<HomeLoaderData>();

  return (
    <main className="HomePage" {...props}>
      <pre>children: {children}</pre>
      <pre>data: {JSON.stringify(loaderData)}</pre>
    </main>
  );
}
