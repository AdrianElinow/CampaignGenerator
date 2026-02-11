import unittest
from .NGIN_AI import *

class Test_NGIN_AI_Planning(unittest.TestCase):

    def setUp(self):
        self.actor = NGIN_Simulae_Actor(generate_person())

        # give actor medicine
        self.actor.Relations[CONTENTS]['medicine'] = SimulaeNode(given_id='medicine', nodetype=OBJ)

    def test_initial_attributes(self):
        self.assertIsNotNone(self.actor)
        self.assertEqual(self.actor.priorities, [])

        print("Test_NGIN_AI","test_initial_attributes:", "PASS")

    def test_NGIN_AI_plan_empty(self):
        self.actor.plan()
        self.assertEqual(self.actor.priorities, [])

        print("Test_NGIN_AI","test_NGIN_AI_plan_empty:", "PASS")

    def test_NGIN_AI_plan_populated(self):

        self.actor.prioritize()

        logDebug("Priorities: ",self.actor.priorities)

        self.actor.plan()

        iterations = 80

        for i in range(iterations) or self.actor.priorities:

            actor_tick_test(self.actor)

            self.actor.prioritize()

            if self.actor.priorities:
                completed_action = self.actor.act_next()
                if completed_action:
                    logDebug("Completed action:", completed_action)
                    self.actor.plan()

        print("Test_NGIN_AI_Planning","test_NGIN_AI_plan_populated:", "PASS")

class Test_NGIN_AI_Socialize(unittest.TestCase):

    def setUp(self):
        self.actor = NGIN_Simulae_Actor(generate_person())

    def test_NGIN_AI_socialize_clone(self):
        # create another actor with whom to socialize
        self.actor_partner = NGIN_Simulae_Actor(generate_person())
        
        # no initial relationship
        self.assertFalse(self.actor.has_relation(self.actor_partner.ID, self.actor_partner.Nodetype))

        # calculate relationship
        relationship = self.actor.determine_relationship(self.actor_partner, interaction=None)
        self.assertIsNotNone(relationship)

        self.assertEqual(relationship[NODETYPE], POI)
        self.assertEqual(relationship[INTERACTIONS], [])
        self.assertEqual(relationship[STATUS], 'new')

        print("Test_NGIN_AI_Socialize","test_NGIN_AI_socialize_clone:", "PASS")


def actor_tick_test(actor):
    # increment all status attributes    
    for attr in actor.Attributes:
        if attr in STATUS_ATTRIBUTES:
            actor.Attributes[attr] += 1

if __name__ == '__main__':
    unittest.main()