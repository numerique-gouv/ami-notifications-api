<script lang="ts">
const FC_AUTHORIZATION_URL = 'https://fcp-low.sbx.dev-franceconnect.fr/api/v2/authorize'

const clickOnFCButton = async () => {
  console.log('clickOnFCButton')
  const response = await fetch(`${FC_AUTHORIZATION_URL}`, {
    method: 'POST',
  })
  console.log('response:', response)
}
</script>

<div>
	<div class="fr-connect-group">
		<button
				class="fr-connect"
				type="button"
				onclick={clickOnFCButton}
		>
			<span class="fr-connect__login">S’identifier avec</span>
			<span class="fr-connect__brand">FranceConnect</span>
		</button>
		<p>
			<a href="https://franceconnect.gouv.fr/" target="_blank" rel="noopener" title="Qu’est-ce que FranceConnect ? - nouvelle fenêtre">Qu’est-ce que FranceConnect ?</a>
		</p>
	</div>
</div>
