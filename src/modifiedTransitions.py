from transitions import *
from transitions.extensions import HierarchicalGraphMachine
from transitions.extensions import GraphMachine
from transitions.extensions.states import add_state_features, Tags
from collections import OrderedDict


@add_state_features(Tags)
class HierarchicalKTS(HierarchicalGraphMachine):
    style_attributes = {
        "node": {
            "": {},
            "default": {
                "style": "rounded, filled",
                "shape": "rectangle",
                "fillcolor": "white",
                "color": "black",
                "peripheries": "1",
            },
            "inactive": {"fillcolor": "white", "color": "black", "peripheries": "1"},
            "parallel": {
                "shape": "rectangle",
                "color": "black",
                "fillcolor": "white",
                "style": "dashed, rounded, filled",
                "peripheries": "1",
            },
            "active": {"color": "black", "fillcolor": "white", "peripheries": "1"},
            "previous": {"color": "blue", "fillcolor": "azure2", "peripheries": "1"},
            "sat": {"color": "green", "fillcolor": "lightgreen", "peripheries": "1"}, #add style for sat/unsat formula
            "unsat": {"color": "red", "fillcolor": "darksalmon", "peripheries": "1"},
        },
        "edge": {"": {}, "default": {"color": "black"}, "previous": {"color": "blue"}},
        "graph": {
            "": {},
            "default": {"color": "black", "fillcolor": "white", "style": "solid"},
            "previous": {"color": "blue", "fillcolor": "azure2", "style": "filled"},
            "active": {"color": "red", "fillcolor": "darksalmon", "style": "filled"},
            "parallel": {"color": "black", "fillcolor": "white", "style": "dotted"},
            "sat": {"color": "green", "fillcolor": "lightgreen", "peripheries": "1"}, #add style for sat/unsat formula
            "unsat": {"color": "red", "fillcolor": "darksalmon", "peripheries": "1"},
        },
    }
    
    def generate_image(self, model):
        self.model_graphs[id(model)].get_graph().draw('src/kts.png', prog='dot')

    
    def get_all_states(self):
        states = self.get_nested_state_names()
        states_dict = OrderedDict()
        for name in states:
            states_dict[name] = self.get_state(name)
        
        return states_dict

    
    def get_updated_dicts(self, states):
        for elem in states:
            new_tags = self.get_state(elem['name']).tags
            elem['tags'] = new_tags
            if 'children' in elem:
                for child in elem['children']:
                    new_tags = self.get_state(elem['name'] + '_' + child['name']).tags
                    child['tags'] = new_tags

        return states
    

    def get_unnested_dicts(self):
        unnested_dicts = []
        for elem in self.get_all_states().items():
            state_dict = {}
            state_dict['name'] = elem[0]
            state_dict['tags'] = elem[1].tags
            unnested_dicts.append(state_dict)
        
        return unnested_dicts
    

    def expanded_structure(self, states, transitions):
        composite_states = []
        for elem in states:
            if 'initial' in elem:
                composite_states.append(elem['name'])
                for t in transitions:
                    if t['dest'] == elem['name']:
                        t['dest'] = elem['name'] + '_' + elem['initial']
        
        new_states = []
        for elem in self.get_unnested_dicts():
            if 'final' in elem['tags']:
                parent = elem['name'].split('_')[0]
                for t in transitions:
                    if t['source'] == parent:
                        t['source'] = elem['name']
            if elem['name'] not in composite_states:
                new_states.append(elem)

        return new_states, transitions
    

    def get_composite_states(self, states):
        composite_states = []
        for elem in states:
            if 'children' in elem:
                composite_states.append(elem['name'])
        
        return composite_states
    

    def non_composite_states(self, states):
        non_comp_states = []
        comp_states = self.get_composite_states(states)
        states = self.get_unnested_dicts()
        
        for elem in states:
            if elem['name'] not in comp_states:
                non_comp_states.append(elem)

        return non_comp_states
    

@add_state_features(Tags)
class GraphKTS(GraphMachine):
    style_attributes = {
        "node": {
            "": {},
            "default": {
                "style": "rounded, filled",
                "shape": "rectangle",
                "fillcolor": "white",
                "color": "black",
                "peripheries": "1",
            },
            "inactive": {"fillcolor": "white", "color": "black", "peripheries": "1"},
            "parallel": {
                "shape": "rectangle",
                "color": "black",
                "fillcolor": "white",
                "style": "dashed, rounded, filled",
                "peripheries": "1",
            },
            "active": {"color": "black", "fillcolor": "white", "peripheries": "1"},
            "previous": {"color": "blue", "fillcolor": "azure2", "peripheries": "1"},
            "sat": {"color": "green", "fillcolor": "lightgreen", "peripheries": "1"}, #add style for sat/unsat formula
            "unsat": {"color": "red", "fillcolor": "darksalmon", "peripheries": "1"},
        },
        "edge": {"": {}, "default": {"color": "black"}, "previous": {"color": "blue"}},
        "graph": {
            "": {},
            "default": {"color": "black", "fillcolor": "white", "style": "solid"},
            "previous": {"color": "blue", "fillcolor": "azure2", "style": "filled"},
            "active": {"color": "red", "fillcolor": "darksalmon", "style": "filled"},
            "parallel": {"color": "black", "fillcolor": "white", "style": "dotted"},
            "sat": {"color": "green", "fillcolor": "lightgreen", "peripheries": "1"}, #add style for sat/unsat formula (composite states use graph style)
            "unsat": {"color": "red", "fillcolor": "darksalmon", "peripheries": "1"},
        },
    }
    
    def generate_image(self, model):
        self.model_graphs[id(model)].get_graph().draw('src/kts.png', prog='dot')


    def get_all_states(self):
        return self.states
    

    def get_updated_dicts(self, states):
        for elem in states:
            new_tags = self.get_state(elem['name']).tags
            elem['tags'] = new_tags

        return states


    def get_composite_states(self, states):
        return []
    

    def non_composite_states(self, states):
        return states
    



class GraphKTS_model():
    pass


