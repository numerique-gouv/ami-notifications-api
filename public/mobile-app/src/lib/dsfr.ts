// This is needed because otherwise we can't test +layout.svelte which imports the DSFR dynamically.
// With this wrapper, we can mock it when we need to write tests.
export async function initDsfr() {
  // @ts-expect-error
  await import('@gouvfr/dsfr/dist/dsfr.module.min.js')
}
