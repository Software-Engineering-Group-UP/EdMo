import unittest
import sys
import os
from collections import OrderedDict

sys.path.insert(1, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
import modifiedTransitions as MT

class TestModifiedTransitions(unittest.TestCase):
    def setUp(self):
        self.states = [{'name': 'Home Page', 'tags': ['l_out']},
          {'name': 'Login', 'tags': ['l_out']},
          {'name': 'Products', 'tags': ['l_in']},
          {'name': 'Product Site', 'tags': ['l_in']},
          {'name': 'Shopping Cart', 'tags': ['l_in']},
          {'name': 'Checkout', 'tags': ['l_in', 'not_empty']},
          {'name': 'Logout', 'tags': ['l_out', 'order_placed']}
          ]
        self.transitions = [{'trigger': 'goto_Login', 'source': 'Home Page', 'dest': 'Login'},
               {'trigger': 'fail', 'source': 'Login', 'dest': 'Login'},
               {'trigger': 'succesfull', 'source': 'Login', 'dest': 'Products'},
               {'trigger': 'see_product', 'source': 'Products', 'dest': 'Product Site'},
               {'trigger': 'back_to_products', 'source': 'Product Site', 'dest': 'Products'},
               {'trigger': 'see_cart', 'source': 'Product Site', 'dest': 'Shopping Cart'},
               {'trigger': 'see_cart', 'source': 'Products', 'dest': 'Shopping Cart'},
               {'trigger': 'back_to_products', 'source': 'Shopping Cart', 'dest': 'Products'},
               {'trigger': 'goto_Checkout', 'source': 'Shopping Cart', 'dest': 'Checkout'},
               {'trigger': 'cancel', 'source': 'Checkout', 'dest': 'Products'},
               {'trigger': 'confirm', 'source': 'Checkout', 'dest': 'Logout'},
               {'trigger': 'reset', 'source': 'Logout', 'dest': 'Home Page'},
               ]
        
        self.hsm_states = [{'name': 'BeforeComp', 'tags': ['p']},
                           {'name': 'CompositeState1', 'tags': [], 'children': [{'name': 'A1', 'tags': ['p']},{'name': 'B1', 'tags': ['q']}, {'name': 'C1', 'tags': ['p', 'q']}], 'initial': 'A1'},
                           {'name': 'CompositeState2', 'tags': [], 'children': [{'name': 'A2', 'tags': ['q']}], 'initial': 'A2'},
                           {'name': 'AfterComp', 'tags': ['p']}]

        self.hsm_transitions = [{'trigger': 'inComp1', 'source': 'BeforeComp', 'dest': 'CompositeState1'},
                                {'trigger': 'inComp2', 'source': 'BeforeComp', 'dest': 'CompositeState2'},
                                {'trigger': 'outComp1', 'source': 'CompositeState1', 'dest': 'AfterComp'},
                                {'trigger': 'outComp2', 'source': 'CompositeState2', 'dest': 'AfterComp'},
                                {'trigger': 'toB1', 'source': 'CompositeState1~A1', 'dest': 'CompositeState1~B1'},
                                {'trigger': 'toC1', 'source': 'CompositeState1~B1', 'dest': 'CompositeState1~C1'},
                                {'trigger': 'outB1', 'dest': 'AfterComp', 'source': 'CompositeState1~B1'},
                                ]
        
        kts = MT.GraphKTS_model()

        hsm_kts = MT.GraphKTS_model()

        self.machine = MT.GraphKTS(model=kts, title="", initial="Home Page", states=self.states,
                                   transitions=self.transitions, show_state_attributes=True)
        
        self.hsm_machine = MT.HierarchicalKTS(model=hsm_kts, title="", initial="BeforeComp", states=self.hsm_states,
                                              transitions=self.hsm_transitions, show_state_attributes=True)
        

    def test_get_all_states(self):
        actual = self.machine.get_all_states().items()
        expected = self.machine.states.items()
        self.assertListEqual(list(actual), list(expected))


    def test_hsm_get_all_states(self):
        actual = self.hsm_machine.get_all_states().items()
        expected = OrderedDict([('BeforeComp', self.hsm_machine.get_state('BeforeComp')),
                                ('CompositeState1', self.hsm_machine.get_state('CompositeState1')),
                                ('CompositeState1~A1', self.hsm_machine.get_state('CompositeState1~A1')),
                                ('CompositeState1~B1', self.hsm_machine.get_state('CompositeState1~B1')),
                                ('CompositeState1~C1', self.hsm_machine.get_state('CompositeState1~C1')),
                                ('CompositeState2', self.hsm_machine.get_state('CompositeState2')),
                                ('CompositeState2~A2', self.hsm_machine.get_state('CompositeState2~A2')),
                                ('AfterComp', self.hsm_machine.get_state('AfterComp'))]).items()
        self.assertListEqual(list(actual), list(expected))

    def test_get_updated_dicts(self):
        for elem in self.machine.states.items():
            elem[1].tags.append('new_tag')
        actual = self.machine.get_updated_dicts(self.states)
        expected = [{'name': 'Home Page', 'tags': ['l_out', 'new_tag'], 'ignore_invalid_triggers': None},
                    {'name': 'Login', 'tags': ['l_out', 'new_tag'], 'ignore_invalid_triggers': None},
                    {'name': 'Products', 'tags': ['l_in', 'new_tag'], 'ignore_invalid_triggers': None},
                    {'name': 'Product Site', 'tags': ['l_in', 'new_tag'], 'ignore_invalid_triggers': None},
                    {'name': 'Shopping Cart', 'tags': ['l_in', 'new_tag'], 'ignore_invalid_triggers': None},
                    {'name': 'Checkout', 'tags': ['l_in', 'not_empty', 'new_tag'], 'ignore_invalid_triggers': None},
                    {'name': 'Logout', 'tags': ['l_out', 'order_placed', 'new_tag'], 'ignore_invalid_triggers': None}
                    ]
        self.assertListEqual(actual, expected)
    

    def test_hsm_get_updated_dicts(self):
        for elem in self.hsm_machine.get_all_states().items():
            elem[1].tags.append('new_tag')
        
        actual = self.hsm_machine.get_updated_dicts(self.hsm_states)
        expected = [{'name': 'BeforeComp', 'tags': ['p', 'new_tag']},
                    {'name': 'CompositeState1', 'tags': ['new_tag'], 'children': [{'name': 'A1', 'tags': ['p', 'new_tag']},{'name': 'B1', 'tags': ['q', 'new_tag']}, {'name': 'C1', 'tags': ['p', 'q', 'new_tag']}], 'initial': 'A1'},
                    {'name': 'CompositeState2', 'tags': ['new_tag'], 'children': [{'name': 'A2', 'tags': ['q', 'new_tag']}], 'initial': 'A2'},
                    {'name': 'AfterComp', 'tags': ['p', 'new_tag']}]
        self.assertListEqual(actual, expected)


    def test_get_composite_states(self):
        actual = self.machine.get_composite_states(self.states)
        expected = []
        self.assertListEqual(actual, expected)

    
    def test_hsm_get_composite_states(self):
        actual = self.hsm_machine.get_composite_states(self.hsm_states)
        expected = ['CompositeState1', 'CompositeState2']
        self.assertListEqual(actual, expected)
    

    def test_non_composite_states(self):
        actual = self.machine.non_composite_states(self.states)
        expected = self.states
        self.assertListEqual(actual, expected)
    

    def test_hsm_non_composite_states(self):
        actual = self.hsm_machine.non_composite_states(self.hsm_states)
        expected = [{'name': 'BeforeComp', 'tags': ['p']},
                    {'name': 'CompositeState1~A1', 'tags': ['p']},
                    {'name': 'CompositeState1~B1', 'tags': ['q']},
                    {'name': 'CompositeState1~C1', 'tags': ['p', 'q']},
                    {'name': 'CompositeState2~A2', 'tags': ['q']},
                    {'name': 'AfterComp', 'tags': ['p']}]
        self.assertListEqual(actual, expected)


    def test_hsm_get_unnested_dicts(self):
        actual = self.hsm_machine.get_unnested_dicts()
        expected = [{'name': 'BeforeComp', 'tags': ['p']},
                    {'name': 'CompositeState1', 'tags': []},
                    {'name': 'CompositeState1~A1', 'tags': ['p']},
                    {'name': 'CompositeState1~B1', 'tags': ['q']},
                    {'name': 'CompositeState1~C1', 'tags': ['p', 'q']},
                    {'name': 'CompositeState2', 'tags': []},
                    {'name': 'CompositeState2~A2', 'tags': ['q']},
                    {'name': 'AfterComp', 'tags': ['p']}]
        self.assertListEqual(actual, expected)
    

    def test_hsm_expanded_structure(self):
        actual = self.hsm_machine.expanded_structure(self.hsm_states, self.hsm_transitions)
        expected = ([{'name': 'BeforeComp', 'tags': ['p']}, {'name': 'CompositeState1~A1', 'tags': ['p']},
                     {'name': 'CompositeState1~B1', 'tags': ['q']}, {'name': 'CompositeState1~C1', 'tags': ['p', 'q']},
                     {'name': 'CompositeState2~A2', 'tags': ['q']}, {'name': 'AfterComp', 'tags': ['p']}],
                    [{'trigger': 'inComp1', 'source': 'BeforeComp', 'dest': 'CompositeState1~A1'},
                     {'trigger': 'inComp2', 'source': 'BeforeComp', 'dest': 'CompositeState2~A2'},
                     {'trigger': 'outComp1', 'source': 'CompositeState1', 'dest': 'AfterComp'},
                     {'trigger': 'outComp2', 'source': 'CompositeState2', 'dest': 'AfterComp'},
                     {'trigger': 'toB1', 'source': 'CompositeState1~A1', 'dest': 'CompositeState1~B1'},
                     {'trigger': 'toC1', 'source': 'CompositeState1~B1', 'dest': 'CompositeState1~C1'},
                     {'trigger': 'outB1', 'dest': 'AfterComp', 'source': 'CompositeState1~B1'}])
        self.assertEqual(actual, expected)
