<script lang="ts">
import {
  PUBLIC_API_URL,
  PUBLIC_FC_BASE_URL,
  PUBLIC_FC_USERINFO_ENDPOINT,
} from '$env/static/public'
import { goto } from '$app/navigation'
import { onMount } from 'svelte'

let userinfo: Object = {}

onMount(async () => {
  try {
    const access_token = localStorage.getItem('access_token')
    const token_type = localStorage.getItem('token_type')
    const id_token = localStorage.getItem('id_token')
    const userinfo_endpoint_headers = {
      Authorization: `${token_type} ${access_token}`,
    }
    const response = await fetch(
      `${PUBLIC_FC_BASE_URL}${PUBLIC_FC_USERINFO_ENDPOINT}`,
      { headers: userinfo_endpoint_headers }
    )
    const userData = await response.json()
    userinfo = userData

    console.log(userData)
  } catch (error) {
    console.error(error)
  }
})

const franceConnectLogout = async () => {
  // The FC logout feature needs the user's browser to be redirected to it.
  // It also needs some token hint that's stored in the session on the backend, so
  // redirect the user to the backend's endpoint, which will in turn redirect to FC.
  window.location = `${PUBLIC_API_URL}/logout`
}
</script>

<div class="homepage-connected">
  <div class="header">
    <div class="header-left">
      <div class="user-profile-container">
        <div class="user-profile">
          AS
        </div>
      </div>
    </div>

    <div class="header-right">
      <div class="message-svg-icon">
        <img src="/remixicons/message-3.svg" alt="Icône de message" />
      </div>

      <div class="notification-svg-icon">
        <img src="/remixicons/notification-3.svg" alt="Icône de notification" />
      </div>
    </div>
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

  <button
      class="fr-connect"
      type="button"
      onclick={franceConnectLogout}
  >
    <span class="fr-connect__login">Se déconnecter de</span>
    <span class="fr-connect__brand">FranceConnect</span>
  </button>

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
  .homepage-connected {
    .header {
      display: flex;
      justify-content: space-between;
      margin-bottom: 24px;

      .user-profile-container {
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
