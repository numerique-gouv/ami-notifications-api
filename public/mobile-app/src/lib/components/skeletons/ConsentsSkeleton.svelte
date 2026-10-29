<div class="skeleton">
  <div class="consents">
    <div class="follow-all-button"></div>
    {#each Array(10).keys() as i}
      <div class="consent-line">
        <div class="lines">
          <div class="line1"></div>
          <div class="line2"></div>
        </div>
        <div class="switch">
          <div class="switch-skeleton"></div>
        </div>
      </div>
    {/each}
  </div>
</div>
<style>
  .skeleton {
    .consents {
      padding: 6rem 1rem 1.5rem 1rem;
    }
    .follow-all-button {
      background: #f5f5fe;
      height: 2.5rem;
      width: 7.4rem;
      margin-top: 1rem;
      margin-bottom: 1rem;
    }
    .consent-line {
      padding: 0.75rem 0 0 0;
      border-bottom: 1px solid #dddddd;
      display: flex;
    }
    .lines {
      flex: 1;
      padding-right: 1rem;
    }
    .switch {
      width: 3.5rem;
      display: flex;
      justify-content: end;
      align-items: top;
    }
    .switch-skeleton {
      background: #ececfe;
      height: 1.5rem;
      border-radius: 1rem;
      width: 3rem;
    }
    .line1 {
      background: #f5f5fe;
      width: 100%;
      height: 1rem;
      margin-bottom: 0.875rem;
    }
    .line2 {
      background: #f5f5fe;
      width: 65%;
      height: 1rem;
      margin-bottom: 0.875rem;
    }
  }
</style>
