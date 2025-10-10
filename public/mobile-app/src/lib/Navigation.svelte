<nav class="menu-footer" aria-label="Menu principal">
  <ul class="menu-list">
    <li class="menu__item">
      <a class="menu__link highlight" href="/" aria-current="true">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="black">
          <path d="M20 20C20 20.5523 19.5523 21 19 21H5C4.44772 21 4 20.5523 4 20V11L1 11L11.3273 1.6115C11.7087 1.26475 12.2913 1.26475 12.6727 1.6115L23 11L20 11V20ZM11 13V19H13V13H11Z"></path>
        </svg>
        <span>Accueil</span>
      </a>
    </li>
    <li class="menu__item">
      <a class="menu__link" href="/">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="black">
          <path d="M9 1V3H15V1H17V3H21C21.5523 3 22 3.44772 22 4V20C22 20.5523 21.5523 21 21 21H3C2.44772 21 2 20.5523 2 20V4C2 3.44772 2.44772 3 3 3H7V1H9ZM20 11H4V19H20V11ZM11 13V17H6V13H11ZM7 5H4V9H20V5H17V7H15V5H9V7H7V5Z"></path>
        </svg>
        <span>Agenda</span>
      </a>
    </li>
    <li class="menu__item">
      <a class="menu__link" href="/">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="black">
          <path d="M8 4H21V6H8V4ZM3 3.5H6V6.5H3V3.5ZM3 10.5H6V13.5H3V10.5ZM3 17.5H6V20.5H3V17.5ZM8 11H21V13H8V11ZM8 18H21V20H8V18Z"></path>
        </svg>
        <span>Listes</span>
      </a>
    </li>
    <li class="menu__item">
      <a class="menu__link" href="/">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="black">
          <path d="M6.41421 15.89L16.5563 5.74785L15.1421 4.33363L5 14.4758V15.89H6.41421ZM7.24264 17.89H3V13.6473L14.435 2.21231C14.8256 1.82179 15.4587 1.82179 15.8492 2.21231L18.6777 5.04074C19.0682 5.43126 19.0682 6.06443 18.6777 6.45495L7.24264 17.89ZM3 19.89H21V21.89H3V19.89Z"></path>
        </svg>
        <span>Demandes</span>
      </a>
    </li>
  </ul>
</nav>

<style>
  nav.menu-footer {
    position: fixed;
    z-index: 2;
    bottom: 0;
    background: var(--background-default-grey);
    border-top: solid 1px var(--background-alt-grey-active);
    width: 100%;

    .menu-list {
      display: flex;
      list-style-type: none;
      padding-inline-start: 0;
      margin-block-start: 0;
      margin-block-end: 0;
    }

    .menu__item {
      padding-bottom: 0;
      width: 100%;

      .menu__link {
        position: relative;
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        background: none;
        padding: .75rem 0 .375rem;
        height: 4.25rem;

        svg {
          fill: var(--blue-france-sun-113-625);
          margin-bottom: .5rem;
          height: 1.5rem;
          width: 1.5rem;
        }

        span {
          display: block;
          width: 100%;
          color: var(--grey-200-850);
          text-align: center;
          font-size: .75rem;
          font-weight: 400;
          line-height: 1.25rem;
        }

        &.highlight {
          &:before {
            z-index: -1;
            content: '';
            position: absolute;
            top: .5rem;
            background: var(--background-contrast-blue-france);
            border-radius: 1rem;
            width: 3.5rem;
            height: 2rem;
          }
        }
      }
    }
  }
</style>
