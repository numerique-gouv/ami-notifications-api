<script lang="ts">
interface Props {
  href: string
  alt?: string
  className?: string
  color?: string
}
let { alt, className, href, color = 'var(--text-default-grey)' }: Props = $props()
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
