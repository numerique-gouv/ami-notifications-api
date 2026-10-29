<script lang="ts">
  import { monthName } from '$lib/agenda';

  let currentDate = new Date();
  let skeletonCurrentMonths: string[] = [];
  let skeletonFutureMonths: string[] = [];
  skeletonCurrentMonths.push(monthName(currentDate));
  let futureDate = new Date(currentDate.getTime() + 30 * 24 * 60 * 60 * 1000);
  if (futureDate.getMonth() !== currentDate.getMonth()) {
    skeletonCurrentMonths.push(monthName(futureDate));
  }
  futureDate.setDate(1);
  [...Array(6)].forEach(() => {
    futureDate.setMonth((futureDate.getMonth() + 1) % 12);
    skeletonFutureMonths.push(monthName(futureDate));
  });
</script>

<div class="skeleton">
  <div class="agenda--events fr-mb-3w">
    <div class="agenda--events--header">
      <h2 class="fr-h6 fr-mb-0 am-text--smbold">Prochainement</h2>
    </div>
    <div class="agenda--events--container current">
      {#each skeletonCurrentMonths as skeletonMonth}
        <p
          class="fr-text--sm fr-mb-0 fr-text-title--grey am-text--smbold agenda--events--month"
        >
          {skeletonMonth}
        </p>
        <div class="agenda--events--container">
          <div class="agenda--item">
            <div class="agenda--item--date">
              <div class="line"></div>
              <div class="line"></div>
            </div>
            <div class="agenda--item--container fr-card fr-card--sm">
              <div class="tag"></div>
              <div class="line"></div>
              <div class="line"></div>
            </div>
          </div>
        </div>
      {/each}
    </div>
  </div>
  <div class="agenda--events">
    <div class="agenda--events--header">
      <h2 class="fr-h6 fr-mb-0 am-text--smbold">Les mois suivants</h2>
    </div>
    <div class="agenda--events--container future">
      {#each skeletonFutureMonths as skeletonMonth}
        <p
          class="fr-text--sm fr-mb-0 fr-text-title--grey am-text--smbold agenda--events--month"
        >
          {skeletonMonth}
        </p>
        <div class="agenda--events--container">
          <div class="agenda--item">
            <div class="agenda--item--date">
              <div class="line"></div>
              <div class="line"></div>
            </div>
            <div class="agenda--item--container fr-card fr-card--sm">
              <div class="tag"></div>
              <div class="line"></div>
              <div class="line"></div>
            </div>
          </div>
        </div>
      {/each}
    </div>
  </div>
</div>

<style>
  .skeleton {
    --border-default-grey: #e5e5e5;
    .agenda--item {
      display: flex;
      position: relative;
      padding: 0.5rem 0;
      .agenda--item--date {
        display: flex;
        flex-direction: column;
        width: 2rem;
        margin-right: 1rem;
      }
      .agenda--item--container {
        flex: 1;
        padding: 0.875rem 2rem 0.875rem 1rem;
      }

      .tag {
        background: #ececfe;
        height: 1.2rem;
        width: 70%;
        margin-bottom: 0.5rem;
      }
      .line {
        background: #f5f5fe;
        margin-bottom: 0.5rem;
        height: 1.2rem;
        &.short {
          width: 70%;
        }
      }
    }
  }
</style>
