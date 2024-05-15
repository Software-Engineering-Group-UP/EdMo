import xml.etree.ElementTree as ET

def read_xml(diagramPath):

    states = []
    transitions = []

    tree = ET.parse(diagramPath)
    root = tree.getroot()
    root = root[0][0][0]

    triggers = []
    ids = []
    connections = []


    for state in root.iter('mxCell'):

        value = state.get('value')
        state_dict = {}

        if value != "" and value != None:
            if state.get('parent') == "1":
                state_dict['name'] = value
                state_dict['tags'] = []
                states.append(state_dict)
                ids.append([value, state.get('id')])
            else:
                triggers.append([value, state.get('parent')])

        elif value == "":
            connections.append([state.get('id'), state.get('source'), state.get('target')])

    
    for elem in triggers:
        transition = {}
        transition['trigger'] = elem[0]
        sourceValue = None
        destValue = None

        for sublist in connections:
            if elem[1] == sublist[0]:
                sourceValue = sublist[1]
                destValue = sublist[2]

        for sublist in ids:
            if sourceValue == sublist[1]:
                transition['source'] = sublist[0]
            if destValue == sublist[1]:
                transition['dest'] = sublist[0]    
        
        transitions.append(transition)


    return states, transitions


