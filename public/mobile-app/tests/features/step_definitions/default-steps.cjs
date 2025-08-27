const { Given,
    Then,
//    When
} = require('@cucumber/cucumber');

Given(
	"l'usager se connecte sur AMI via France Connect en tant que {string} et suit le process de france connexion",
	function (s) {
		// Write code here that turns the phrase above into concrete actions
	}
);

Given("l'usager est sur la home page non connectée de l'application AMI", function () {
	// Write code here that turns the phrase above into concrete actions
});

Then("l'usager devrait arriver sur la home page connectée de l'application AMI", function () {
	// Write code here that turns the phrase above into concrete actions
});

Then(
	"l'usager {string} devrait être notifiable",
	function (s) {
		console.log(s);
	}
);