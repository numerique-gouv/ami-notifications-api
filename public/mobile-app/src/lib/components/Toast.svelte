<script lang="ts">
  import {
    type DurationType,
    Toast,
    type ToastType,
    toastStore,
  } from '$lib/state/toast.svelte';

  interface Props {
    id: string;
    title: string;
    toastType: ToastType;
    duration: DurationType | null;
    hasCloseLink: boolean;
  }
  let { id, title, toastType, duration, hasCloseLink }: Props = $props();
  let toast: Toast;

  $effect(() => {
    toast = new Toast(id, title, toastType, duration, hasCloseLink);
  });
</script>

<div class="fr-notice toast-wrapper {toastType}">
  <div class="toast-body">
    <div class="toast-body-left-wrapper">
      {#if toastType === 'success'}
        <span class="success fr-icon-success-fill" aria-hidden="true"></span>
      {:else if toastType === 'info'}
        <span class="info fr-icon-error-warning-fill" aria-hidden="true"></span>
      {:else if toastType === 'warning'}
        <span class="warning fr-icon-warning-fill" aria-hidden="true"></span>
      {:else if toastType === 'error'}
        <span class="error fr-icon-close-circle-fill" aria-hidden="true"></span>
      {:else}
        <span class="info fr-icon-error-warning-fill" aria-hidden="true"></span>
      {/if}
      <p>{title}</p>
    </div>
    <div class="toast-body-right-wrapper">
      {#if hasCloseLink}
        <button
          onclick={() => toastStore.removeToast(id)}
          aria-label="Fermer le toast"
          data-testid="close-button"
        >
          <span class="fr-icon-close-line" aria-hidden="true"></span>
        </button>
      {/if}
    </div>
  </div>
</div>

<style>
  .toast-wrapper {
    border-radius: 0.25rem;
    color: var(--grey-50-1000);
    padding: 12px 0.5rem;
    margin-top: 1rem;
    &.success {
      background-color: var(--green-emeraude-975-75);
    }
    &.info {
      background-color: var(--info-950-100);
    }
    &.warning {
      background-color: var(--yellow-moutarde-950-100);
    }
    &.error {
      background-color: var(--error-950-100);
    }
    .toast-body {
      display: flex;
      justify-content: space-between;
      .toast-body-left-wrapper {
        display: flex;
        span {
          margin-right: 0.5rem;
          &.success::before {
            background-color: var(--success-425-625);
          }
          &.info::before {
            background-color: var(--info-425-625);
          }
          &.warning::before {
            background-color: var(--warning-425-625);
          }
          &.error::before {
            background-color: var(--error-425-625);
          }
        }
        p {
          font-size: 14px;
        }
      }
      button {
        font-size: 14px;
        color: var(--blue-france-sun-113-625);
      }
    }
  }
</style>
