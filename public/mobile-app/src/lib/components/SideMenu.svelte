<script lang="ts">
  import { goto } from '$app/navigation';

  let { sideMenus } = $props();
</script>

<div>
  <nav class="fr-sidemenu am-sidemenu fr-mb-3w fr-mx-0">
    <div class="fr-sidemenu__inner">
      <ul class="fr-sidemenu__list" data-testid="steps">
        {#if sideMenus}
          {#each sideMenus as item}
            <li class="fr-sidemenu__item">
              <button
                class="
                  fr-sidemenu__btn fr-pl-0 am-text--smbold
                  {item.iconClass}
                  {item.iconClass && 'fr-tag--icon-left'}
                  {item.tag ? 'fr-pr-9w': 'fr-pr-4w'} "
                type="button"
                data-testid="service-steps-{item.id}"
                onclick={()=> goto(item.url)}
              >
                <span class="am-sidemenu-details">
                  {#if item.date}
                    <span
                      class="am-sidemenu-date fr-text--xs fr-text--regular fr-text-mention--grey"
                      >{item.date}
                    </span>
                  {/if}
                  <span class="am-sidemenu-label">{item.title}</span>
                  {#if item.desc}
                    <span
                      class="am-sidemenu-description fr-text--sm fr-text--regular fr-text-mention--grey"
                      >{item.desc}
                    </span>
                  {/if}
                </span>
                {#if item.tag}
                  <p
                    class="fr-tag fr-tag--sm fr-background-action-low--blue-france am-text--smbold"
                  >
                    {item.tag}
                  </p>
                {/if}
                <span
                  aria-hidden="true"
                  class="icon fr-icon-arrow-right-s-line am-color-blue    "
                ></span>
              </button>
            </li>
          {/each}
        {/if}
      </ul>
    </div>
  </nav>
</div>

<style lang="scss">

  .am-sidemenu {
    &.fr-sidemenu {
      box-shadow:
        inset 0 -1px 0 0 var(--border-default-grey),
        inset 0 0 0 0 var(--border-default-grey);
      .fr-sidemenu__btn {
        min-height: 4.5rem;

        &:before {
          margin-right: 0.5rem;
        }
      }

      .icon {
        position: absolute;
        right: 0;
        top: 50%;
        transform: translateY(-50%);
      }

      .am-sidemenu-details {
        display: flex;
        flex-direction: column;
      }

      .fr-tag {
        position: absolute;
        right: 1.75rem;
        top: 50%;
        transform: translateY(-50%);
      }

    }
  }
</style>
