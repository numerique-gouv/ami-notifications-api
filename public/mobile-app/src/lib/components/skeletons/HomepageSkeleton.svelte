<script lang="ts">
  import { AMIGoto } from '$lib/ami-navigation';
</script>
<div class="skeleton">
  <div class="rubrique-container">
    <div class="autopromo fr-p-2w">
      <div class="icon"></div>
      <div class="line"></div>
      <div class="line"></div>
    </div>
  </div>
  <div class="rubrique-container agenda-container">
    <div class="header-container fr-mb-1w">
      <h2 class="fr-h6 fr-mb-0 am-text--smbold title">Mon agenda</h2>
      <button
        type="button"
        class="fr-link fr-icon-arrow-right-line fr-link--icon-right am-link-icon-xl"
        aria-label="Voir tous mes évènements"
        onclick={() => AMIGoto("/#/agenda")}
      ></button>
    </div>
    <div class="fr-card agenda">
      <div class="tag"></div>
      <div class="line"></div>
      <div class="line"></div>
    </div>
  </div>
  <div class="rubrique-container followup-container">
    <div class="header-container fr-mb-1w">
      <h2 class="fr-h6 fr-mb-0 am-text--smbold title">Mes démarches</h2>
      <button
        type="button"
        class="fr-link fr-icon-arrow-right-line fr-link--icon-right am-link-icon-xl"
        aria-label="Voir toutes mes démarches"
        onclick={() => AMIGoto("/#/followup")}
      ></button>
    </div>
    <div class="fr-card followup">
      <div class="tag"></div>
      <div class="date"></div>
      <div class="line"></div>
      <div class="line"></div>
      <div class="line short"></div>
    </div>
  </div>
</div>

<style lang="scss">
    .rubrique-container {
      &:not(:last-child) {
        margin-bottom: 1.5rem;
      }
      .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
      }
      }

  .skeleton {
    --border-default-grey: #e5e5e5;
    .autopromo {
      background: #ececfe;
      height: 10rem;
      .icon {
        margin: 0 auto;
        height: 3rem;
        width: 3rem;
        border-radius: 100%;
        background: #e3e3fd;
      }
      .line {
        background: #e3e3fd;
        margin: 0.5rem 0;
        height: 1.2rem;
      }
    }
    .agenda {
      padding: .875rem 1rem;
      .tag {
        background: #ececfe;
        height: 1.2rem;
        width: 50%;
      }
      .line {
        background: #f5f5fe;
        margin-top: 0.5rem;
        height: 1.2rem;
      }
    }
    .followup {
      position: relative;
      padding: .875rem 1rem;
      border-bottom: .25rem solid var(--border-active-blue-france);
      .tag {
        background: #ececfe;
        height: 1.2rem;
        width: 50%;
      }
      .date {
        background: #f5f5fe;
        height: 0.8rem;
        width: 30%;
        position: absolute;
        top: .875rem;
        right: 1rem;
      }
      .line {
        background: #f5f5fe;
        margin-top: 0.5rem;
        height: 1.2rem;
        &.short {
          width: 70%;
        }
      }
    }
  }
</style>
