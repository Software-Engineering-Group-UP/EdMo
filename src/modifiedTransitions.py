from transitions import *
from transitions.extensions import HierarchicalGraphMachine
from transitions.extensions import GraphMachine
from transitions.extensions.states import add_state_features, Tags, Timeout
from collections import OrderedDict


@add_state_features(Tags, Timeout)
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
    

    def get_substates(self):
        subs = list(set(self.get_all_states().items()) - set(self.states.items()))
        sub_dicts = []
        for s in subs:
            names = s[0].split('_')
            parent = names[0]
            child = names[1]
            match = 0
            for entry in sub_dicts:
                if entry['name'] == parent:
                    entry['children'].append({'name': child, 'tags': s[1].tags})
                    match = 1
            if match == 0:
                sub_dicts.append({'name': parent, 'tags': self.get_state(parent).tags, 'children': [{'name': child, 'tags': s[1].tags}]})
        
        return sub_dicts


    
    def get_updated_dicts(self):
        composite_states = self.get_substates()
        updated_states = []
        for elem in self.states.items():
            match = 0
            for comp in composite_states:
                if elem[0] == comp['name']:
                    updated_states.append(comp)
                    match = 1
            if match == 0:
                state_dict = {}
                state_dict['name'] = elem[0]
                state_dict['tags'] = elem[1].tags
                updated_states.append(state_dict)
        
        return updated_states
    

    def get_unnested_dicts(self):
        unnested_dicts = []
        for elem in self.get_all_states().items():
            state_dict = {}
            state_dict['name'] = elem[0]
            state_dict['tags'] = elem[1].tags
            unnested_dicts.append(state_dict)
        
        return unnested_dicts
    

@add_state_features(Tags, Timeout)
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
    
    def get_updated_dicts(self):
        updated_states = []
        for elem in self.get_all_states().items():
            state_dict = {}
            state_dict['name'] = elem[0]
            state_dict['tags'] = elem[1].tags
            updated_states.append(state_dict)
        
        return updated_states
    
    def get_unnested_dicts(self):
        return self.get_updated_dicts()


class GraphKTS_model():
    pass


