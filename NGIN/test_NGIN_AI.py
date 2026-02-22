import unittest

from NGIN.NGIN_Socialization import RESPONSE_WEIGHTS, SOCIAL_INTERACTION_QUALIFIERS, SOCIAL_INTERACTION_TYPES
from .NGIN_AI import *

class Test_NGIN_AI_Planning(unittest.TestCase):

    def setUp(self):
        self.actor = NGIN_Simulae_Actor(generate_person())

        # give actor medicine
        #self.actor.Relations[CONTENTS]['medicine'] = SimulaeNode(given_id='medicine', nodetype=OBJ)

    def test_initial_attributes(self):
        self.assertIsNotNone(self.actor)
        self.assertEqual(self.actor.priorities, [])

    def test_NGIN_AI_plan_empty(self):
        self.actor.plan()
        self.assertEqual(self.actor.priorities, [])

    def test_NGIN_AI_plan_populated(self):
        return # todo ae: fix


        self.actor.prioritize()

        logAll("Priorities: ",self.actor.priorities)

        self.actor.plan()

        iterations = 80

        for i in range(iterations) or self.actor.priorities:

            actor_tick_test(self.actor)

            self.actor.prioritize()

            if self.actor.priorities:
                completed_action = self.actor.act_next()
                if completed_action:
                    logAll("Completed action:", completed_action)
                    self.actor.plan()

class Test_NGIN_AI_Socialize(unittest.TestCase):

    def setUp(self):
        self.actor = NGIN_Simulae_Actor(generate_person())
        self.actor_partner = NGIN_Simulae_Actor(generate_person())

    def test_NGIN_AI_socialize_clone(self):
        # no initial relationship
        self.assertFalse(self.actor.has_relation(self.actor_partner.ID, self.actor_partner.Nodetype))

        # calculate relationship
        relationship = self.actor.determine_relationship(self.actor_partner, interaction=None)

        if not relationship:
            self.fail("Relationship should not be None")

        self.assertIsNotNone(relationship)
        self.assertEqual(relationship[NODETYPE], POI)
        self.assertEqual(relationship[INTERACTIONS], [])
        self.assertEqual(relationship[STATUS], 'new')

    def test_NGIN_AI_appraise_social_event(self):
        # create a social event
        social_event = {
            'eventtype': 'greet',
            'qualifiers': { qualifier: factors[0] for qualifier, factors in SOCIAL_INTERACTION_QUALIFIERS.items() }
        }
        
        # iterate through ALL social event types and validate appraisal
        for social_event_type in SOCIAL_INTERACTION_TYPES:
    
            social_event['eventtype'] = social_event_type
            # also update qualifiers        

            # appraise the social event
            appraisal = self.actor.appraise_social_event(social_event)

            if not appraisal:
                self.fail("Appraisal should not be None")

            self.assertIsNotNone(appraisal)

            # Todo AE: add additional assertions


    def test_NGIN_AI_select_response(self):
        # create a social event
       

        pass


def actor_tick_test(actor: SimulaeNode):
    # increment all status attributes    
    for attr in actor.Attributes:
        if attr in STATUS_ATTRIBUTES:
            attribute_value = actor.get_attribute(attr)

            if not attribute_value:
                attribute_value = 0

            actor.set_attribute(attr, attribute_value + 1)

if __name__ == '__main__':
    unittest.main()