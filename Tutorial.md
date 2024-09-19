# EdMo - Tutorial

- to start, select "File" from the top menu and either import or load a diagram
- the diagram can be moved around or zoomed with the mouse or the "+" and "-" buttons on the top
- the layout can be changed between "TopBottom" or "LeftRight" in the top menu

- in the top left section you can see a table where you can manage atomic propositions (APs)
    - APs can be added, changed and deleted with the "Edit" button
    - you can make changes directly in the table, individual propositions need to be seperated with a comma
    - changes can be confirmed with the "Done" button, the table and diagram will then be updated
    - APs can be highlighted in the diagram with the "Highlight" button

- in the bottom left section you can manage CTL-Formulas
    - CTL-Formulas can be added, edited and deleted
    - when adding or editing formulas, you can choose which states the formula should be applied to
    - to verify a formula you have to check the Box next to it and then use the "Check" button
    - the diagram and formula will change colors according to the results
    - for a failed check, the states causing the failure will be listed below the formula
    - you can reset all markings with the "Reset" Button on the top right
    - Optionally, a description can be given for each formula, it can be viewed with the "Description" button

----------------------------------------------------------

### Rules for writing CTL-Formulas:
- you can use the standard logic operators: ~ (not), & (and), | (or), => (imply), <=> (iff)
- you can use the CTL specific path operators (A, E) and state operators (X, F, G, U)
- a path operators needs to be immediatly followed by a state operator
- the binary operator U is an exception to the rule above and can be preceeded by a proposition

Examples:

AG(EF(ReferenceBehavior | released))

E ~available U returned

- you can specify a subset of actions to be checked by adding them directly after the state operator in curly brackets:

    AF{confirm | reset | cancel} l_out

----------------------------------------------------------

### Creating your own diagrams with draw.io:
You can create and import your own diagrams with https://www.drawio.com/. When you create your own diagrams, you need to follow a few rules:
- you can use the shapes for state machine diagrams in the UML category, they are marked in red
- you need to make sure that state names are unique and don't use the "~" symbol in any names
- you can add triggers to edges by double clicking on them
- make sure all of the states and edges are connected correctly
- you can export your finished diagram as an xml file and add it to your EdMo/examples/ folder

Nested states:
- if you want to add nested states, make sure to use the "Composite State" shape
- you can place all the substates inside the composite state
- make sure to add a "start" and "end" shape insinde the composite state as well

