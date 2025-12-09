<script lang="ts">
import type { Snippet } from 'svelte'
import Icon from '$lib/components/Icon.svelte'

interface Props {
  id?: string
  children?: Snippet
  iconHref: string
  className?: string
  title: string
}
let { children, className, iconHref, id, title }: Props = $props()
</script>

<div {id} class="fr-card fr-p-3w fr-mb-2w fr-enlarge-link {className}">
  <div class="fr-card__body fr-p-0">
    <div class="fr-card__content fr-p-0 fr-m-0">
      <h3 class="fr-card__title">
        <Icon className="fr-mr-2v" href={iconHref} />
        {title}
      </h3>
      <p class="fr-card__desc ">
        {@render children?.()}
      </p>
    </div>
  </div>
</div>

<style>
.fr-card__title {
  align-items: center;
  display: flex;
  flex-direction: row;
}
</style>
