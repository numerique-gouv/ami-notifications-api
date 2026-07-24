<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/state';
  import {
    PUBLIC_API_URL,
    PUBLIC_FEATURE_FLAG_FI_LOGIN_ENABLED,
  } from '$env/static/public';
  import { AMIGoto } from '$lib/ami-goto';
  import { franceConnectLogout } from '$lib/france-connect';

  let data_providers: Record<string, unknown> = $state({});
  let datas: Record<string, Record<string, unknown>> = $state({});
  let selected: string = $state('');
  const fi_enabled = PUBLIC_FEATURE_FLAG_FI_LOGIN_ENABLED === 'true';

  onMount(async () => {
    if (!fi_enabled) {
      AMIGoto('/');
      return;
    }
    try {
      const response = await fetch(
        `${PUBLIC_API_URL}/api/v1/authentication/providers/`
      );
      data_providers = await response.json();
      selected = Object.keys(data_providers)[0];
    } catch {}
    const searchParams = page.url.searchParams;
    if (searchParams.has('is_logged_in')) {
      if (
        localStorage.getItem('id_token') === null &&
        searchParams.get('id_token') !== ''
      ) {
        localStorage.setItem('id_token', searchParams.get('id_token') || '');
      }
      Object.keys(data_providers).forEach((key) => {
        const encoded_data = searchParams.get(key) || '';
        if (encoded_data) {
          try {
            datas[key] = JSON.parse(atob(encoded_data));
          } catch (error) {
            console.error(error);
          }
        }
      });
    }
  });

  const AMIFILogin = async () => {
    const id_token_hint = localStorage.getItem('id_token') || '';
    const redirect_url = `${PUBLIC_API_URL}/login-ami-fi?provider_id=${selected}`;
    if (id_token_hint) {
      await franceConnectLogout(id_token_hint, redirect_url);
    } else {
      window.location.href = redirect_url;
    }
  };
</script>

{#each Object.entries(data_providers) as [key, label], i}
  <div class="fr-radio-group" data-testid="radio-{key}">
    <input
      type="radio"
      id="{key}"
      value="{key}"
      name="data-provider"
      bind:group={selected}
    >
    <label class="fr-label" for="{key}">{label}</label>
  </div>
{/each}

<div>
  <button class="fr-connect" type="button" id="fr-connect-button" onclick={AMIFILogin}>
    Test AMI-FI
  </button>
</div>

{#each Object.entries(datas) as [key, data], i}
  {#if Object.keys(data).length}
    <section class="fr-accordion">
      <h3 class="fr-accordion__title">
        <button
          type="button"
          class="fr-accordion__btn"
          aria-expanded="false"
          aria-controls="accordion-{key}"
        >
          {data_providers[key]}
        </button>
      </h3>
      <div id="accordion-{key}" class="fr-collapse">
        <pre data-testid="{key}">{ JSON.stringify(data, null, 2) }</pre>
      </div>
    </section>
  {/if}
{/each}
