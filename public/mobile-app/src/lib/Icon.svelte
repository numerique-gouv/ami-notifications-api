<script lang="ts">
interface Props {
  href: string
  alt: string
  className: string
}
let { alt, className, href }: Props = $props()
</script>

<span class="icon {className}" style="--svg: url('{href}')"></span>

<style>
.icon {
  background-color: var(--text-active-blue-france);
  mask: var(--svg) no-repeat center;
  mask-size: contain;
  width: 20px;
  height: 20px;
}
</style>
