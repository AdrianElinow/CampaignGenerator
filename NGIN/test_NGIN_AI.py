import unittest
from NGIN.NGIN_AI import *

class Test_NGINAI(unittest.TestCase):

    def setUp(self):
        self.actor = NGIN_Simulae_Actor(generate_individual())

    def test_initial_attributes(self):
        self.assertIsNotNone(self.actor.SimulaeNode)
        self.assertEqual(self.actor.priorities, [])

    def test_NGIN_AI_plan_empty(self):
        self.actor.plan()
        self.assertEqual(self.actor.priorities, [])

    def test_NGIN_AI_plan_populated(self):

        self.actor.plan()

        iterations = 100

        for i in range(iterations) or self.actor.priorities:
            print(f"\n#### #### #### #### {i} #### #### #### #### \n")
        
            actor_tick_test(self.actor)

            print(self.actor.status_summary())

            completed_action = self.actor.act_next()
            if completed_action:
                print("Completed action:", completed_action)
                self.actor.plan()
        

def actor_tick_test(actor):
    # decrement all status attributes    
    for attr in actor.SimulaeNode.attributes:
        if attr in STATUS_ATTRIBUTES:
            actor.SimulaeNode.attributes[attr] -= 1



if __name__ == '__main__':
    unittest.main()