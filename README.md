# EdMo
The aim of this project is to develop a model checker suitable for teaching software engineering. 
The application can be used to import and display state machine diagrams, assign atomic propositions and CTL formulas, as well as verifying them with a model checking algorithm.

The model checker currently supports the import of state machine diagrams in an XML format. In the examples folder you can find state machine diagrams that were constructed using [draw.io](https://www.drawio.com/) and exported as XML files.

The model checker uses features of the [transitions](https://github.com/pytransitions/transitions) library. Therefore this library and its diagram extension must be installed in order to run the application. In addition the application uses the [pytl](https://github.com/fpom/pytl) Parser to parse CTL formlas.

### License
---
This project is licensed under a [MIT license](/LICENSE.md).
