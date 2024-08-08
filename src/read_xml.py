import xml.etree.ElementTree as ET
import re


def translate_forkJoin(forkJoins, connections):
    for elem in forkJoins:
            for con in connections:
                if elem['id'] == con[1]:
                    elem['sources'].append(con) # sources contains all connections, that have fj as source
                if elem['id'] == con[2]:
                    elem['targets'].append(con) # targets contains all connections, that have fj as target

    new_connections = []

    for elem in forkJoins:
        for con in connections:
            if con in elem['targets']: # con is ingoing transition for fork/join
                con[2] = elem['sources'][0][2] # set node after fj as target
                for i in range(1,len(elem['sources'])):
                    new_connections.append([con[0], con[1], elem['sources'][i][2]]) # make new connection with every node after fj
            if con in elem['sources']: # con is outgoing transition for fork/join
                con[1] = elem['targets'][0][1] # set node before fj as source
                for i in range(1,len(elem['targets'])):
                    new_connections.append([con[0], elem['targets'][i][1], con[2]]) # make new connection with every node before fj

    connections += new_connections

    return connections


def add_initialChild(states, connections, startElements, substates):
    initial_children = []
    for con in connections: # find all initial substates
        if con[1] in startElements:
            for sub in substates:
                if con[2] == sub['id']:
                    initial_children.append([sub['name'], sub['parent']])
                    break
    
    for elem in states: # add entry for initial in composite state
        if 'children' in elem:
            for child in initial_children:
                if child[1] == elem['name']:
                    elem['initial'] = child[0]

    return states


def tag_final_children(states, connections, endElements, substates):
    final_children = []
    for con in connections: # find all final substates
        if con[2] in endElements:
            for sub in substates:
                if con[1] == sub['id']:
                    final_children.append(sub['name'])

    for elem in states:
        if 'children' in elem:
            for child in elem['children']:
                if child['name'] in final_children:
                    child['tags'] = ['final']

    return states


def translate_CompositeStates(states, connections, ids, compStates, possibleChildren, startElements, endElements):
    substates = []
    for elem in compStates:
        for con in connections: # make sure all connections connect to composite state and not it's subtitle
            if con[1] == elem['subspace']:
                con[1] = elem['id']
            if con[2] == elem['subspace']:
                con[2] = elem['id']

        children = []
        for state in possibleChildren: # check if states are placed inside composite state
            geometry = state.find('mxGeometry')
            child_x = int(geometry.get('x'))
            child_y = int(geometry.get('y'))

            if (elem['x'] < child_x < (elem['x'] + elem['w'])) and (elem['y'] < child_y < (elem['y'] + elem['h'])):
                children.append({'name': state.get('value'), 'tags': []})
                substates.append({'id': state.get('id'), 'name': state.get('value'), 'parent': elem['name']})

        elem['children'] = children
    

    for elem in states: # add list of children to composite state
        for comp in compStates:
            if elem['name'] == comp['name']:
                elem['children'] = comp['children']

    sub_list = list(map(lambda sub: sub['name'], substates))
    states = list(filter(lambda elem: elem['name'] not in sub_list, states)) # remove substates, they are now children of other states

    for elem in ids: # change ids to reflect substate naming convention
        for sub in substates: 
            if elem[0] == sub['name']:
                elem[0] = sub['parent'] + '~' + elem[0]

    states = add_initialChild(states, connections, startElements, substates)
    states = tag_final_children(states, connections, endElements, substates)

    return states, connections


def find_initial(states, connections, ids, startElements):
    possibleInitial = []
    for con in connections:
        if con[1] in startElements:
            for elem in ids:
                if con[2] == elem[1]:
                    possibleInitial.append(elem)

    initial = None
    for elem in possibleInitial:
        for state in states:
            if state['name'] == elem[0]:
                initial = state['name']

    return initial


def read_xml(diagramPath):

    states = []
    transitions = []

    tree = ET.parse(diagramPath)
    root = tree.getroot()
    root = root[0][0][0]

    connections = []
    triggers = []
    ids = []
    startElements = []
    endElements = []
    forkJoins = []
    compStates = []
    possibleChildren = []

    for state in root.iter('mxCell'):

        value = state.get('value')
        state_dict = {}
        style = state.get('style')
        if style == None:
            style = ""

        if re.search(".*shape=startState.*", style):
            startElements.append(state.get('id'))

        elif re.search(".*shape=endState.*", style):
            endElements.append(state.get('id'))

        elif re.search("shape=line.*", style): # shape=line indicates fork/join element
            forkJoins.append({'id': state.get('id'), 'sources': [], 'targets': []})

        elif re.search("swimlane.*", style): # swimlane indicates Composite State element
            geometry = state.find('mxGeometry')
            x = int(geometry.get('x'))
            y = int(geometry.get('y'))
            w = int(geometry.get('width'))
            h = int(geometry.get('height'))
            compStates.append({'name': value, 'id': state.get('id'), 'subspace': '', 'x': x, 'y': y, 'w': w, 'h': h})
            state_dict['name'] = value
            state_dict['tags'] = []
            states.append(state_dict)
            ids.append([value, state.get('id')])

        elif re.search("text.*", style): # find corresponding subspace for composite state
            for comp in compStates:
                if state.get('parent') == comp['id']:
                    comp['subspace'] = state.get('id')

        elif value != "" and value != None:
            if state.get('parent') == "1" and state.get('vertex'):  # element is a state
                state_dict['name'] = value
                state_dict['tags'] = []
                states.append(state_dict)
                ids.append([value, state.get('id')])
                possibleChildren.append(state)
            elif state.get('parent') == "1" and state.get('edge'): # element is transition with guard
                triggers.append([value, state.get('id')])
                connections.append([state.get('id'), state.get('source'), state.get('target')])
            else: # element is transition label
                triggers.append([value, state.get('parent')])

        elif (value == "" or not value) and state.get('edge'): # element is transition without direct label
            connections.append([state.get('id'), state.get('source'), state.get('target')])


    connections = translate_forkJoin(forkJoins, connections) # turn fork/joins into normal connections

    states, connections = translate_CompositeStates(states, connections, ids, compStates, possibleChildren, startElements, endElements)

    initial = find_initial(states, connections, ids, startElements)

    for con in connections: # connect trigger, source and dest to form transition
        transition = {}

        for trig in triggers:
            if con[0] == trig[1]:
                transition['trigger'] = trig[0]

        if transition:
            for elem in ids:
                if con[1] == elem[1]:
                    transition['source'] = elem[0]
                if con[2] == elem[1]:
                    transition['dest'] = elem[0]
            transitions.append(transition)

    return states, transitions, initial
