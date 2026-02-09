import unittest
from .NGIN_AI import *

class Test_NGINAI(unittest.TestCase):

    def setUp(self):
        self.actor = NGIN_Simulae_Actor(generate_individual())
        self.actor.SimulaeNode.Relations[CONTENTS]['medicine'] = SimulaeNode(given_id='medicine', nodetype=OBJ)

    def test_initial_attributes(self):
        self.assertIsNotNone(self.actor.SimulaeNode)
        self.assertEqual(self.actor.priorities, [])
        print("test_initial_attributes:", "PASS")

    def test_NGIN_AI_plan_empty(self):
        self.actor.plan()
        self.assertEqual(self.actor.priorities, [])
        print("test_NGIN_AI_plan_empty:", "PASS")

    def test_NGIN_AI_plan_populated(self):

        self.actor.prioritize()

        print("Priorities: ",self.actor.priorities)

        self.actor.plan()

        iterations = 80

        for i in range(iterations) or self.actor.priorities:

            actor_tick_test(self.actor)

            self.actor.prioritize()

            if self.actor.priorities:
                completed_action = self.actor.act_next()
                if completed_action:
                    print("Completed action:", completed_action)
                    self.actor.plan()

        print("test_NGIN_AI_plan_populated:", "PASS")
        

def actor_tick_test(actor):
    # increment all status attributes    
    for attr in actor.SimulaeNode.Attributes:
        if attr in STATUS_ATTRIBUTES:
            actor.SimulaeNode.Attributes[attr] += 1

if __name__ == '__main__':
    unittest.main()