import xml.etree.ElementTree as ET
import re

def read_xml(diagramPath):

    states = []
    transitions = []

    tree = ET.parse(diagramPath)
    root = tree.getroot()
    root = root[0][0][0]

    triggers = []
    ids = []
    connections = []
    forkJoins = []


    for state in root.iter('mxCell'):

        value = state.get('value')
        state_dict = {}
        style = state.get('style')
        if style == None:
            style = ""

        if re.search("shape=line.*", style): # shape=line indicates fork/join element
            forkJoins.append({'id': state.get('id'), 'sources': [], 'targets': []})

        elif value != "" and value != None:
            if state.get('parent') == "1" and state.get('vertex'):  # element is a state
                state_dict['name'] = value
                state_dict['tags'] = []
                states.append(state_dict)
                ids.append([value, state.get('id')])
            elif state.get('parent') == "1" and state.get('edge'): # element is transition with guard
                triggers.append([value, state.get('id')])
                connections.append([state.get('id'), state.get('source'), state.get('target')])
            else: # element is transition label
                triggers.append([value, state.get('parent')])
        
        elif (value == "" or not value) and state.get('edge'): # element is transition without direct label
            connections.append([state.get('id'), state.get('source'), state.get('target')])


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

    for con in connections:
        transition = {}

        for trig in triggers:
            if con[0] == trig[1]:
                transition['trigger'] = trig[0]
        
        if transition:
            for sublist in ids:
                if con[1] == sublist[1]:
                    transition['source'] = sublist[0]
                if con[2] == sublist[1]:
                    transition['dest'] = sublist[0]
            transitions.append(transition)


    return states, transitions


