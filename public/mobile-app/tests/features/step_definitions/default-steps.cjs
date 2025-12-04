const { Given, When, Then, Before, After, setDefaultTimeout, context } = require("@cucumber/cucumber");

const { chromium, expect, defineConfig } = require("@playwright/test");

const { Page } = require("playwright");

setDefaultTimeout(60 * 1000);

let page, browserContext, browser;

Before(async function () {
	browser = await chromium.launch(
		//uncomment this line to see the tests in live
		//{ headless: false, slowMo: 1500}
	);
	browserContext = await browser.newContext(
		//{baseURL: "https://localhost:4173/", ignoreHTTPSErrors: true}
		{baseURL: "https://ami-back-staging.osc-fr1.scalingo.io/"}
	);
	page = await browserContext.newPage();
});

After(async function () {
	await browserContext.close();
	await browser.close();
})

Given(
	"l'usager se connecte sur AMI via France Connect en tant que {string} et suit le process de france connexion",
	async (s) => {
		await page.locator('#fr-connect-button').click()
		await page.getByTestId('idp-e1e90d50-cca0-4a85-9db3-0bcc190ee6f7').click()
		await page.getByLabel('Mot de passe').fill('123')
		await page.getByRole('button', {name: 'Valider'}).click()
		await page.getByRole('button', {name: 'Continuer sur AMI'}).click()
	}
);

Given("l'usager est sur la home page non connectée de l'application AMI", async () => {
		await page.goto("/")
});

Then("l'usager devrait arriver sur la home page connectée de l'application AMI", async () => {
	await expect(page.locator('.user-profile')).toBeVisible()
});

Then("les données de l'usager {string} récupérées depuis l'API Particulier devraient être affichées", function (s) {
	//console.log(s);
});

Then("l'usager {string} devrait être enregistré(e)", function (s) {
	//console.log(s);
});