<script lang="ts">
  import { onMount } from 'svelte';
  import {
    PUBLIC_PARTNERS_17CYBER_DOMAIN,
    PUBLIC_PARTNERS_17CYBER_MODE,
    PUBLIC_PARTNERS_17CYBER_TOKEN,
  } from '$env/static/public';

  interface WidgetConfig {
    token: string;
    domainName: string;
    mode: string;
    description?: string;
    width?: string;
    height?: string;
    frameColor?: string;
    frameTitleColor?: string;
  }

  // Les paramètres facultatifs peuvent rester vides ou être retirés.
  // Les couleurs doivent être renseignées au format hexadécimal (ex. '#FF0000' ou '#F00')
  const widgetConfig: WidgetConfig = {
    token: PUBLIC_PARTNERS_17CYBER_TOKEN,
    domainName: PUBLIC_PARTNERS_17CYBER_DOMAIN,
    mode: PUBLIC_PARTNERS_17CYBER_MODE, // Obligatoire : div ou page
    description: '', // Facultatif : Titre du cadre
    width: '100%', // Facultatif : Largeur de la div, en % ou px, max. 400px (mode div)
    height: '90%', // Facultatif : Hauteur de la div, en % ou px (mode div)
    frameColor: '#000091', // Facultatif : Couleur du cadre (mode div)
    frameTitleColor: '', // Facultatif : Couleur du titre du cadre (mode div)
  };
  onMount(() => {
    const head = document.getElementsByTagName('head')[0];

    const link = document.createElement('link');
    link.href = `https://${widgetConfig.domainName}/build-widget/style.css`;
    link.rel = 'stylesheet';
    head.appendChild(link);

    const styleScript = document.createElement('script');
    styleScript.src = `https://${widgetConfig.domainName}/build-widget/style.js`;
    styleScript.type = 'text/javascript';
    head.appendChild(styleScript);

    const appScript = document.createElement('script');
    appScript.src = `https://${widgetConfig.domainName}/build-widget/app.js`;
    appScript.type = 'text/javascript';
    appScript.onload = () => {
      (
        window as unknown as Window & { loadWidget: (config: WidgetConfig) => void }
      ).loadWidget(widgetConfig);
    };
    head.appendChild(appScript);
  });
</script>

{#if PUBLIC_PARTNERS_17CYBER_MODE == "page"}
  <div class="am-widget-iframe-container">
    <div id="widgetIframe"></div>
  </div>
{/if}

<style>
  .am-widget-iframe-container {
    height: calc(100vh - 0.5rem);
    #widgetIframe {
      margin-top: 0;
      padding: 0;
    }
  }
</style>
