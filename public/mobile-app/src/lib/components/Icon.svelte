<script lang="ts">
  interface Props {
    href: string
    className?: string
    color?: string
  }
  let { className, href, color = 'var(--text-default-grey)' }: Props = $props()
</script>

<span class="icon {className}" style="--svg: url('{href}'); --icon-color: {color};"></span>

<style>
.icon {
  background-color: var(--icon-color);
  display: inline-block;
  mask: var(--svg) no-repeat center;
  mask-size: contain;
  width: 20px;
  height: 20px;
}
</style>
