<script lang="ts">
  import { AMIGoto } from '$lib/ami-navigation';
  import NavWithBackButton from '$lib/components/NavWithBackButton.svelte';

  let backUrl: string = '/#/step';
</script>

<div class="fr-container step-page-form">
  <NavWithBackButton className="small-header" title="Je deviens parent" {backUrl}>
    <div class="settings-svg-icon"></div>
  </NavWithBackButton>
  <div class="fr-pt-8w fr-pb-10w">
    <div class="fr-stepper am-stepper">
      <div class="fr-stepper__title"><span class="fr-stepper__state">1/6</span></div>
      <div class="fr-stepper__steps" data-fr-current-step="1" data-fr-steps="9"></div>
    </div>

    <fieldset
      class="fr-fieldset step-form"
      id="radio"
      aria-labelledby="radio-legend radio-messages"
    >
      <legend
        class="fr-fieldset__legend--regular fr-fieldset__legend"
        id="radio-legend"
      >
        <h2 class="fr-h3">Quelle est votre situation ?</h2>
      </legend>
      <div class="fr-fieldset__element">
        <div class="fr-radio-group">
          <input value="1" type="radio" id="radio-1" name="radio">
          <label
            class="fr-label fr-p-3w fr-text--lg fr-mb-0 am-text--smbold"
            for="radio-1"
          >
            Mon conjoint dépend du régime général
          </label>
        </div>
      </div>
      <div class="fr-fieldset__element">
        <div class="fr-radio-group">
          <input value="2" type="radio" id="radio-2" name="radio">
          <label
            class="fr-label fr-p-3w fr-text--lg fr-mb-0 am-text--smbold"
            for="radio-2"
          >
            Je vais avoir mon premier enfant
          </label>
        </div>
      </div>
      <div class="fr-messages-group" id="radio-messages" aria-live="polite"></div>
    </fieldset>
  </div>
  <div class="fr-p-2w footer">
    <button
      type="button"
      class="fr-btn fr-btn--tertiary-no-outline fr-icon-arrow-left-line fr-btn--icon-left"
    >
      Précédent
    </button>
    <button
      type="button"
      class="fr-btn fr-btn--tertiary-no-outline fr-icon-arrow-right-line fr-btn--icon-right"
    >
      suivant
    </button>
  </div>
</div>

<style lang="scss">
  .step-page-form {
    position: relative;
    .footer {
      position: fixed;
      bottom: 0;
      left: 0;
      width: 100%;
      min-height: 5rem;
      display: flex;
      justify-content: space-between;
      background-color: var(--grey-1000-50);
    }
  }
  .fr-stepper.am-stepper {
    .fr-stepper__state {
      display: block;
      text-align: right;
    }
    .fr-stepper__steps {
      --stepper-size: 0px;
      height: .25rem;
      border-radius: 4px;
    }
  }
  .step-form {
    .fr-radio-group {
      max-width: inherit;
      input[type=radio]+label {
        display: block;
        width: 100%;
        background: none;
        border-radius: .25rem;
        border: solid 1px var(--grey-900-175);
        &:before {
          height: 100%;
          width: 100%;
          border-radius: 0;
          margin: 0;
          left: 0;
        }
      }
      input[type=radio]:checked+label {
        background: var(--blue-france-925-125);
        border-color: var(--blue-france-925-125);
      }
    }
  }
</style>
