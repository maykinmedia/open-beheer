export type CatalogiLoaderData = {
  catalogiChoices: CatalogiChoice[];
};

/**
 * Catalogi loader.
 * Loader data can be obtained using `useLoaderData()` in CatalogiPage.
 */
export async function catalogiLoader(): Promise<CatalogiLoaderData> {
  // await login("julian", "julian", undefined);
  // const serviceChoices = await getServiceChoices();
  // const catalogiChoices = await getCatalogiChoices(serviceChoices[0].value);
  // return {
  //   catalogiChoices,
  // };
}
