<script lang="ts">
  import capture_ajout_icone from '$lib/assets/installation/ajout_icone.png';
  import capture_ajouter_ecran_accueil from '$lib/assets/installation/ajouter_ecran_accueil.png';
  import capture_ecran_accueil from '$lib/assets/installation/ecran_accueil.png';
  import capture_nom_app from '$lib/assets/installation/nom_app.png';
  import capture_partager from '$lib/assets/installation/partager.png';
</script>

<div>
  <p>
    👉 Si vous avez déjà installé l'application AMI, merci de fermer cet onglet et de
    lancer l'application depuis votre écran d'accueil 👈
  </p>

  <hr>

  <h1>Installation de l'application AMI</h1>

  <p>
    Pour utiliser l'application AMI, il vous faut tout d'abord l'ajouter à votre écran
    d'accueil.
  </p>

  <ol>
    <li>
      <img
        src={capture_partager}
        alt="Capture d'écran du bouton partager"
        style="width: 200px; margin: 20px;"
      >
      cliquez sur le bouton "partager" en bas de votre écran
    </li>
    <li>
      <img
        src={capture_ecran_accueil}
        alt="Capture d'écran de l'ajout à l'écran d'accueil"
        style="width: 200px; margin: 20px;"
      >
      Sélectionnez "Sur l'écran d'accueil"
    </li>
    <li>
      <img
        src={capture_nom_app}
        alt="Capture d'écran du choix du nom de l'application"
        style="width: 200px; margin: 20px;"
      >
      Choisissez un nom pour l'application, ou laissez "AMI"
    </li>
    <li>
      <img
        src={capture_ajouter_ecran_accueil}
        alt="Capture d'écran du bouton d'ajout de l'icône sur l'écran d'accueil"
        style="width: 200px; margin: 20px;"
      >
      Cliquez sur "Ajouter" tout en haut à droite de votre écran
    </li>
    <li>
      <img
        src={capture_ajout_icone}
        alt="Capture d'écran de l'icône de l'application sur l'écran d'accueil"
        style="width: 200px; margin: 20px;"
      >
      Fermez votre navigateur pour afficher votre écran d'accueil, cliquez sur la
      nouvelle icône que vous venez d'installer
    </li>
  </ol>

  <p>🥳 C'est réussi !</p>

  <hr>

  <p>
    👉 Si vous arrivez à nouveau sur cette page à l'avenir, nul besoin de réinstaller
    l'application si elle est toujours présente sur votre écran d'accueil, il suffira de
    fermer votre navigateur et de relancer AMI depuis votre écran d'accueil ! 👈
  </p>
</div>

<style>
  li {
    margin: 0 1em;
    width: 100%;
  }
</style>
