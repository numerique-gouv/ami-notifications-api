# Contributing to Behavior-Driven Development

## Distinguishing BDD from Automated Testing
It is important to distinguish between **BDD** and **automated testing**. Automated tests usually come later in the process: they are heavier to maintain, require a significant amount of code, and can easily lead to legacy issues. They are most valuable in complex cases, such as when dealing with combinatorial business rules or integrating multiple heterogeneous components.  

BDD, on the other hand, is useful from the very beginning. By fostering collaboration between developers, testers, and business stakeholders to produce Gherkin scenarios, it encourages early and detailed conversations. As Liz Keogh put it: *“Having conversations is more important than capturing conversations, which in turn is more important than automating conversations.”*  

## Contributing as a business people

This project uses [Cucumber](https://cucumber.io/) and Gherkin for behavior-driven development. Below are instructions for setting up your environment and working with feature files.

### 1. Setting Up VS Code

1. **Install [Visual Studio Code](https://code.visualstudio.com/).**
2. **Install the "Cucumber (Gherkin) Full Support" plugin by Alexander Krechik:**
    - Open VS Code.
    - Go to Extensions (`Ctrl+Shift+X`).
    - Search for `Cucumber (Gherkin) Full Support`.
    - Click **Install**.

### 2. Feature Files Location

- All Gherkin feature files are located in the `public/mobile-app/tests/features` directory.

### 3. Step Autocompletion

- The plugin provides autocompletion for steps if they are registered in your step definition files.
- When writing scenarios, start typing a step and suggestions will appear if the step exists.

## Contributing as a developer

No IDE is recommended over another, instructions are provided below to help you 
integrate everything into your preferred IDE. Feel free to complete this section with tips, feedback, or 
instructions specific to other development environments you use. 

### PyCharm

The following plugins have been tested

- **Cucumber.js** (for JavaScript step definitions)
- **Gherkin** (for syntax highlighting and autocompletion)

Don't forget to tag the language in the first line of the feature file if a language other than English is used.

To launch a Cucumber scenario from PyCharm, don't use a ~~Behave~~ configuration but a **Cucumber.js** configuration, 
after having launched `npm install` if needed.

## 5. Launching Acceptance Tests

Currently, there is no automated test execution integrated into the CI/CD pipeline. However, you can manually run acceptance tests 
- using **PyCharm** with the Cucumber.js and Gherkin plugins installed : After having launched `npm install` if needed, simply open your feature files in PyCharm and use the provided tools to execute and debug your scenarios. Don't use a ~~Behave~~ configuration but a **Cucumber.js** configuration.
- in a **terminal** : go to directory `/public/mobile-app directory` and launch `npx cucumber-js tests/features` or `npm run test:cucumber`.
