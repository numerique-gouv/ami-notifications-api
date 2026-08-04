<script lang="ts">
  interface Props {
    className?: string;
  }
  let { className }: Props = $props();
</script>

<span class="icon {className}"></span>

<style>
  .icon {
    display: inline-block;
    width: 1.25rem;
    height: 1.25rem;
    flex-shrink: 0;

    &:before {
      display: block;
    }
  }
</style>
