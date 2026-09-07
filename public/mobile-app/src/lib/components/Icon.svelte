<script lang="ts">
  interface Props {
    className?: string;
  }
  let { className }: Props = $props();
</script>

<span aria-hidden="true" class="icon {className}"></span>

<style>
  .icon {
    display: inline-block;
    flex-shrink: 0;

    &:before {
      display: block;
    }
  }
</style>
