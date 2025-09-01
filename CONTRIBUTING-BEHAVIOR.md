# Contributing to Behavior-Driven Development

This project uses [Cucumber](https://cucumber.io/) and Gherkin for behavior-driven development. Below are instructions for setting up your environment and working with feature files.

## 1. Setting Up VS Code

1. **Install [Visual Studio Code](https://code.visualstudio.com/).**
2. **Install the "Cucumber (Gherkin) Full Support" plugin by Alexander Krechik:**
    - Open VS Code.
    - Go to Extensions (`Ctrl+Shift+X`).
    - Search for `Cucumber (Gherkin) Full Support`.
    - Click **Install**.

## 2. Feature Files Location

- All Gherkin feature files are located in the `public/mobile-app/tests/features` directory.

## 3. Step Autocompletion

- The plugin provides autocompletion for steps if they are registered in your step definition files.
- When writing scenarios, start typing a step and suggestions will appear if the step exists.

## 4. Using PyCharm

Developers can also use [PyCharm](https://www.jetbrains.com/pycharm/) with the following plugins:

- **Cucumber.js** (for JavaScript step definitions)
- **Gherkin** (for syntax highlighting and autocompletion)

To install plugins in PyCharm:

1. Go to `File > Settings > Plugins`.
2. Search for `Cucumber.js` and `Gherkin`.
3. Click **Install**.

## 5. Launching Acceptance Tests

Currently, there is no automated test execution integrated into the CI/CD pipeline. However, you can manually run acceptance tests using PyCharm with the Cucumber.js and Gherkin plugins installed. Simply open your feature files in PyCharm and use the provided tools to execute and debug your scenarios.

## 6. Tips

Don't forget to tag the language in the first line of the feature file if a language other than English is used.
