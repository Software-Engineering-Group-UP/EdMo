import unittest
from src.KripkeTransitionSystem import *
from src.tlParser import *
from src.mc_algorithm import *

class TestMCAlgorithm(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        states = [{'name': 'Home Page', 'tags': ['l_out']},
          {'name': 'Login', 'tags': ['l_out']},
          {'name': 'Products', 'tags': ['l_in']},
          {'name': 'Product Site', 'tags': ['l_in']},
          {'name': 'Shopping Cart', 'tags': ['l_in']},
          {'name': 'Checkout', 'tags': ['l_in', 'not_empty']},
          {'name': 'Logout', 'tags': ['l_out', 'order_placed']},
          ]
        transitions = [{'trigger': 'goto_Login', 'source': 'Home Page', 'dest': 'Login'},
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

        self.kts = KripkeTransitionSystem(states=states, transitions=transitions, initial="Home Page")
    
    def test_True(self):
        self.assertSetEqual(check_bool(mc_parse("True"), self.kts), {'Home Page', 'Product Site', 'Logout', 'Shopping Cart', 'Login', 'Checkout', 'Products'})

    def test_False(self):
        self.assertSetEqual(check_bool(mc_parse("False"), self.kts), set())
    
    def test_Atom(self):
        self.assertSetEqual(check_atom(mc_parse("l_in"), self.kts), {'Checkout', 'Products', 'Product Site', 'Shopping Cart'})
    
    def test_Not(self):
        self.assertSetEqual(check_not(mc_parse("~l_in"), self.kts), {'Login', 'Logout', 'Home Page'})

    def test_And(self):
        self.assertSetEqual(check_and(mc_parse("l_in & not_empty"), self.kts), {'Checkout'})

    def test_Or(self):
        self.assertSetEqual(check_or(mc_parse("l_in | l_out"), self.kts), {'Products', 'Shopping Cart', 'Home Page', 'Login', 'Logout', 'Checkout', 'Product Site'})

    def test_Imply1(self):
        self.assertSetEqual(check_imply(mc_parse("not_empty => l_in"), self.kts), {'Products', 'Login', 'Checkout', 'Product Site', 'Home Page', 'Shopping Cart', 'Logout'})
    
    def test_Imply2(self):
        self.assertSetEqual(check_imply(mc_parse("l_in => not_empty"), self.kts), {'Login', 'Home Page', 'Logout', 'Checkout'})

    def test_Iff(self):
        self.assertSetEqual(check_iff(mc_parse("l_in <=> not_empty"), self.kts), {'Login', 'Home Page', 'Logout', 'Checkout'})

    def test_EX1(self):
        self.assertSetEqual(check_EX(mc_parse("EX l_out"), self.kts), {'Checkout', 'Home Page', 'Login', 'Logout'})

    def test_EX2(self):
        self.assertSetEqual(check_EX(mc_parse("EX{reset | confirm | cancel} l_out"), self.kts), {'Logout', 'Checkout'})

    def test_EX3(self):
        self.assertSetEqual(check_EX(mc_parse("EX{reset} l_out"), self.kts), {'Logout'})

    def test_AX1(self):
        self.assertSetEqual(check_AX(mc_parse("AX l_out"), self.kts), {'Home Page', 'Logout'})

    def test_AX2(self):
        self.assertSetEqual(check_AX(mc_parse("AX{reset | confirm | cancel} l_out"), self.kts), {'Logout'})

    def test_EF1(self):
        self.assertSetEqual(check_EF(mc_parse("EF l_out"), self.kts), {'Logout', 'Products', 'Home Page', 'Shopping Cart', 'Product Site', 'Checkout', 'Login'})

    def test_EF2(self):
        self.assertSetEqual(check_EF(mc_parse("EF{fail | goto_Login | successful} l_out"), self.kts), {'Home Page', 'Logout', 'Login'})

    def test_AF1(self):
        self.assertSetEqual(check_AF(mc_parse("AF l_in"), self.kts), {'Products', 'Checkout', 'Product Site', 'Shopping Cart'})

    def test_AF2(self):
        self.assertSetEqual(check_AF(mc_parse("AF{confirm | reset | cancel} l_out"), self.kts), {'Logout', 'Login', 'Home Page'})

    def test_AF3(self):
        self.assertSetEqual(check_AF(mc_parse("AF{confirm | reset} l_out"), self.kts), {'Checkout', 'Logout', 'Login', 'Home Page'})

    def test_EG1(self):
        self.assertSetEqual(check_EG(mc_parse("EG l_in"), self.kts), {'Checkout', 'Products', 'Shopping Cart', 'Product Site'})

    def test_EG2(self):
        self.assertSetEqual(check_EG(mc_parse("EG{confirm} l_in"), self.kts), {'Products', 'Shopping Cart', 'Product Site'})

    def test_AG1(self):
        self.assertSetEqual(check_AG(mc_parse("AG l_in"), self.kts), set())

    def test_AG2(self):
        self.assertSetEqual(check_AG(mc_parse("AG{see_product | see_cart | back_to_products} l_in"),  self.kts), {'Product Site', 'Products', 'Checkout', 'Shopping Cart'})

    def testEU1(self):
        self.assertSetEqual(check_EU(mc_parse("E l_in U order_placed"), self.kts), {'Products', 'Shopping Cart', 'Product Site', 'Logout', 'Checkout'})

    def testEU2(self):
        self.assertSetEqual(check_EU(mc_parse("E l_in U l_out"), self.kts), {'Products', 'Shopping Cart', 'Product Site', 'Logout', 'Login', 'Checkout', 'Home Page'})

    def testEU3(self):
        self.assertSetEqual(check_EU(mc_parse("E l_in U{goto_Checkout | confirm} order_placed"), self.kts), {'Checkout', 'Shopping Cart', 'Logout'})

    def testAU1(self):
        self.assertSetEqual(check_AU(mc_parse("A l_in U order_placed"), self.kts), {'Logout'})

    def testAU2(self):
        self.assertSetEqual(check_AU(mc_parse("A l_in U l_out"), self.kts), {'Login', 'Home Page', 'Logout'})

    def testAU3(self):
        self.assertSetEqual(check_AU(mc_parse("A l_in U{goto_Checkout | confirm} order_placed"), self.kts), {'Logout', 'Shopping Cart', 'Checkout'})

    def test_formula1(self):
        self.assertSetEqual(check_formula(mc_parse("l_in & ~not_empty"), self.kts), {'Products', 'Product Site', 'Shopping Cart'})

    def test_formula2(self):
        self.assertSetEqual(check_formula(mc_parse("~(l_in & not_empty)"), self.kts), {'Products', 'Home Page', 'Login', 'Logout', 'Product Site', 'Shopping Cart'})

    def test_formula3(self):
        self.assertSetEqual(check_formula(mc_parse("~(not_empty => l_in)"), self.kts), set())

    def test_formula4(self):
        self.assertSetEqual(check_formula(mc_parse("(EX ~l_in) & not_empty"), self.kts), {'Checkout'})

