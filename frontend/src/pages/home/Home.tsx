import "./Home.css";

export type HomePageProps = React.ComponentProps<"main"> & {
  // Props here.
};

/**
 * Home page
 */
export function HomePage({ children, ...props }: HomePageProps) {
  return (
    <main className="HomePage" {...props}>
      {children}
    </main>
  );
}
