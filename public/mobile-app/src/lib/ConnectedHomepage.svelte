<script lang="ts">
import {
  PUBLIC_APP_URL,
  PUBLIC_FC_BASE_URL,
  PUBLIC_FC_LOGOUT_ENDPOINT,
} from '$env/static/public'
import { onMount } from 'svelte'

let userinfo: Object = $state({})
let isMenuDisplayed = $state(false)

function parseJwt(token) {
  const base64Url = token.split('.')[1]
  const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
  const jsonPayload = decodeURIComponent(
    window
      .atob(base64)
      .split('')
      .map(function (c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)
      })
      .join('')
  )

  return JSON.parse(jsonPayload)
}

onMount(async () => {
  try {
    const access_token = localStorage.getItem('access_token')
    const token_type = localStorage.getItem('token_type')
    const id_token = localStorage.getItem('id_token')
    const userData = localStorage.getItem('user_data')
    userinfo = parseJwt(userData)

    console.log(userinfo)
  } catch (error) {
    console.error(error)
  }
})

const toggleMenu = () => {
  isMenuDisplayed = !isMenuDisplayed
}

const franceConnectLogout = async () => {
  const params = new URLSearchParams({
    id_token_hint: localStorage.getItem('id_token') || '',
    state: 'not-implemented-yet-and-has-more-than-32-chars',
    post_logout_redirect_uri: `${PUBLIC_APP_URL}/?is_logged_out`,
  })
  const url = new URL(`${PUBLIC_FC_BASE_URL}${PUBLIC_FC_LOGOUT_ENDPOINT}`)
  url.search = params.toString()
  window.location = url.toString()
}
</script>

<div class="homepage-connected">
  <div class="header">
    <button class="header-left" onclick={toggleMenu}>
      <span class="user-profile">
        AS
      </span>
    </button>

    <div class="header-right">
      <div class="message-svg-icon">
        <img src="/remixicons/message-3.svg" alt="Icône de message" />
      </div>

      <div class="notification-svg-icon">
        <img src="/remixicons/notification-3.svg" alt="Icône de notification" />
      </div>
    </div>
  </div>

  <div class="menu {isMenuDisplayed ? '' : 'is-hidden'}">
    <button
        class="fr-connect-logout"
        type="button"
        onclick={franceConnectLogout}
    >
      <span>Me déconnecter</span>
    </button>
  </div>

  <div class="rubrique-container qr-code-scan-container">
    <div class="rubrique-content-container">
      <div class="fr-tile fr-tile-sm fr-tile--horizontal fr-enlarge-link">
        <div class="fr-tile__body">
          <div class="fr-tile__content">
            <img class="qr-code-icon" src="/remixicons/qr-code.svg" alt="Icône de QR code" />
            <h3 class="fr-tile__title">
              <a href="/">Scanner le QR code d'un service partenaire</a>
            </h3>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div class="rubrique-container">
    <div class="header-container">
      <span class="title">Mes rendez-vous</span>
      <a title="Voir toutes mes rendez-vous" href="/">
        <span class="see-all">Voir tout</span>
        <img class="arrow-line" src="/remixicons/arrow-line.svg" alt="Icône de flèche" />
      </a>
    </div>
    <div class="rubrique-content-container">
      <div class="fr-tile fr-tile-sm fr-tile--horizontal fr-enlarge-link">
        <div class="fr-tile__body">
          <div class="fr-tile__content">
            <h3 class="fr-tile__title">
              <a href="/#/rdv/">2 août 2025 à 15H15</a>
            </h3>
            <p class="fr-tile__desc">Rendez-vous dans votre Agence France Travail Paris 18e Ney</p>
            <div class="fr-tile__start">
              <p class="fr-badge">
                <img src="/remixicons/calendar-event-line.svg" alt="Icône de calendrier" />
                RDV
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div class="rubrique-container">
    <div class="header-container">
      <span class="title">Mes échéances</span>
      <a title="Voir toutes les échéances" href="/">
        <span class="see-all">Voir tout</span>
        <img class="arrow-line" src="/remixicons/arrow-line.svg" alt="Icône de flèche" />
      </a>
    </div>
    <div class="rubrique-content-container">
      <div class="fr-tile fr-tile-sm fr-tile--horizontal fr-enlarge-link">
        <div class="fr-tile__body">
          <div class="fr-tile__content">
            <h3 class="fr-tile__title">
              <a href="/">Ramassage encombrants</a>
            </h3>
            <p class="fr-tile__desc">Le ramassage mensuel des encombrants aura lieu ce jeudi 4 avril</p>
            <div class="fr-tile__start">
              <p class="fr-badge">
                <img src="/dsfr-v1.14.0/icons/buildings/bank-line.svg" alt="Icône de banque" />
                Municipalité
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div class="rubrique-container">
    <div class="header-container">
      <span class="title">Mes demandes</span>
      <a title="Voir toutes les demandes" href="/">
        <span class="see-all">Voir tout</span>
        <img class="arrow-line" src="/remixicons/arrow-line.svg" alt="Icône de flèche" />
      </a>
    </div>
    <div class="rubrique-content-container">
      TODO
    </div>
  </div>

  <section class="fr-accordion">
    <h3 class="fr-accordion__title">
      <button type="button" class="fr-accordion__btn" aria-expanded="false" aria-controls="accordion-1">Données de debug</button>
    </h3>
    <div id="accordion-1" class="fr-collapse">
      <ul>
        <li>userinfo: <pre>{ JSON.stringify(userinfo, null, 2) }</pre></li>
        <li>sub: { userinfo.sub }</li>
        <li>given_name: { userinfo.given_name }</li>
        <li>given_name_array: { userinfo.given_name_array }</li>
        <li>family_name: { userinfo.family_name }</li>
        <li>birthdate: { userinfo.birthdate }</li>
        <li>gender: { userinfo.gender }</li>
        <li>birthplace: { userinfo.birthplace }</li>
        <li>birthcountry: { userinfo.birthcountry }</li>
        <li>email: { userinfo.email }</li>
        <li>aud: { userinfo.aud }</li>
        <li>exp: { userinfo.exp }</li>
        <li>iat: { userinfo.iat }</li>
        <li>iss: { userinfo.iss }</li>
      </ul>
    </div>
  </section>

  <nav class="fr-nav" aria-label="Menu principal">
    <ul class="fr-nav__list">
      <li class="fr-nav__item">
        <img class="arrow-line" src="/remixicons/home-4-fill.svg" alt="Icône de flèche" />
        <a class="fr-nav__link" href="/" target="_self" aria-current="page">Accueil</a>
      </li>
      <li class="fr-nav__item">
        <img class="arrow-line" src="/remixicons/calendar-event-line.svg" alt="Icône de flèche" />
        <a class="fr-nav__link" href="/" target="_self">Échéancier</a>
      </li>
      <li class="fr-nav__item">
        <img class="arrow-line" src="/remixicons/list-check.svg" alt="Icône de flèche" />
        <a class="fr-nav__link" href="/" target="_self">Listes</a>
      </li>
      <li class="fr-nav__item">
        <img class="arrow-line" src="/remixicons/edit-line.svg" alt="Icône de flèche" />
        <a class="fr-nav__link" href="/" target="_self">Demandes</a>
      </li>
    </ul>
  </nav>
</div>

<style>
  .is-hidden {
    display: none;
  }

  .homepage-connected {
    .header {
      display: flex;
      justify-content: space-between;
      margin-bottom: 24px;

      .header-left {
        display: flex;
        justify-content: center;
        align-items: center;

        height: 48px;
        width: 48px;
        border-radius: 50%;
        background-color: var(--blue-france-925-125-hover);

        .user-profile {
          font-size: 18px;
          font-weight: 500;
          line-height: 28px;
          color: var(--blue-france-sun-113-625);
        }
      }

      .header-right {
        display: flex;
        align-items: center;

        .message-svg-icon {
          margin-right: 16px;
        }
      }
    }

    .menu {
      position: absolute;
      z-index: 1000;
      margin-top: -20px;
      padding: 8px;
      background-color: white;
      border-radius: 4px;
      box-shadow: 2px 2px 2px gray;

      .fr-connect-logout {
        padding: 8px 12px;

        font-size: 14px;
        line-height: 24px;
      }
    }

    .qr-code-scan-container {
      .fr-tile {
        background-color: var(--blue-france-950-100);

        .fr-tile__content {
          display: flex;
          flex-direction: row;
          align-items: center;

          img {
            margin-right: 24px;
          }

          .fr-tile__title {
            margin-bottom: 0;

            a {
              color: var(--grey-50-1000);
              font-size: 16px;
              font-weight: 500;
              line-height: 24px;
            }
          }
        }
      }
    }

    .rubrique-container {
      margin-bottom: 24px;

      .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;

        .title {
          font-size: 18px;
          font-weight: 500;
          line-height: 28px;
        }

        .see-all {
          font-size: 14px;
          font-weight: 400;
          line-height: 24px;
          color: var(--blue-france-sun-113-625);
          margin-right: 4px;
        }
      }

      .rubrique-content-container {
        .fr-tile {
          .fr-badge {
            font-size: 12px;
            font-weight: 700;
            line-height: 20px;
            color: var(--success-425-625);
            background-color: var(--green-bourgeon-975-75);

            img {
              width: 12px;
              margin-right: 4px;
            }
          }
        }
      }
    }

    .fr-accordion {
      margin-bottom: 24px;
    }

    nav {
      .fr-nav__list {
        flex-direction: row;
        justify-content: space-around;

        .fr-nav__item::before {
           content: none;
        }

        .fr-nav__item {
          align-items: center;

          img {
            width: 24px;
          }

          a {
            color: var(--grey-200-850);
            font-size: 12px;
            font-weight: 400;
            line-height: 20px;
          }
        }
      }
    }
  }
</style>
