<script lang="ts">
import Icon from '$lib/components/Icon.svelte'

interface Props {
  iconHref: string
  className?: string
  title: string
}
let { className, iconHref, title }: Props = $props()
</script>

<div class="fr-card fr-p-3w fr-mb-2w fr-enlarge-link">
  <div class="fr-card__body fr-p-0">
    <div class="fr-card__content fr-p-0 fr-m-0">
      <h3 class="fr-card__title">
        <Icon className="fr-mr-2v" href={iconHref} />
        {title}
      </h3>
      <p class="fr-card__desc ">
        <slot />
      </p>
    </div>
  </div>
</div>

<style>
.fr-card__title {
  align-items: center;
  display: flex;
  flex-direction: row;
  a {
    color: var(--text-default-grey);
  }
}
</style>



