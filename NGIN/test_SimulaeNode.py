import unittest

from .SimulaeNode import *

class Test_SimulaeNode(unittest.TestCase):

    def test_init_POI(self):

        node = SimulaeNode(nodetype=POI)

        self.assertIsNotNone(node.ID)
        self.assertEqual(node.Nodetype, POI)

        self.assertEqual(node.Status, Status.ALIVE)

        self.assertIsNotNone(node.References)
        
        references_keys = node.References.keys()
        self.assertIn(NAME, references_keys)
        self.assertIn(POLICY, references_keys)
        self.assertIn(PERSONALITY, references_keys)
        self.assertIsNotNone(node.References[POLICY])
        self.assertIsNotNone(node.References[PERSONALITY])
        self.assertIsNotNone(node.Attributes)

        self.assertIsNotNone(node.Relations)
        for relation, relatives in node.Relations.items():
            self.assertIn(relation, RELATIVE_TYPES)
            relations_keys = relatives.keys()
            self.assertEqual(list(relations_keys).sort(), NODETYPES.sort())

            for nt, items in relatives.items():
                self.assertEqual(items, {})
        
        print("test_init_POI:", "PASS")

    def test_init_OBJ(self):

        node = SimulaeNode()

        self.assertIsNotNone(node.ID)
        self.assertEqual(node.Nodetype, OBJ)

        self.assertEqual(node.Status, Status.ALIVE)

        self.assertIsNotNone(node.References)
        
        references_keys = node.References.keys()
        self.assertIn(NAME, references_keys)
        self.assertIsNotNone(node.Attributes)

        self.assertIsNotNone(node.Relations)
        for relation, relatives in node.Relations.items():
            self.assertIn(relation, RELATIVE_TYPES)
            relations_keys = relatives.keys()
            self.assertEqual(list(relations_keys).sort(), NODETYPES.sort())

            for nt, items in relatives.items():
                self.assertEqual(items, {})

        print("test_init_OBJ:", "PASS")

    def test_summary(self):
        print("test_summary:","NOT IMPLEMENTED")
        return #todo AE: fix this test
        
    def test_str_(self):
        node = SimulaeNode(given_id="test_node", nodetype=POI, references={NAME: "Test Node"})
        self.assertNotEqual(str(node), "")

    def test_add_adjacent_location(self):
        print("test_add_adjacent_location:","NOT IMPLEMENTED")
        return #todo AE: fix this test

    def test_get_adjacent_locations(self):
        node = SimulaeNode(given_id="node", nodetype=LOC, references={ADJACENT: ["loc1", "loc2"]})
        adjacents = node.get_adjacent_locations()
        self.assertIn("loc1", adjacents)
        self.assertIn("loc2", adjacents)

    def test_knows_about(self):
        print("test_knows_about:","NOT IMPLEMENTED")
        return #todo AE: fix this test

    def test_get_reference(self):
        node = SimulaeNode(given_id="node", references={NAME: "Test Node"})
        self.assertEqual(node.get_reference(NAME), "Test Node")
        print("test_get_reference:", "PASS")

    def test_add_reference(self):
        print("test_add_reference:","NOT IMPLEMENTED")
        return #todo AE: fix this test

    def test_get_attribute(self):
        node = SimulaeNode(given_id="node", attributes={"interactions": 5})
        self.assertEqual(node.get_attribute("interactions"), 5)
        print("test_get_attribute:", "PASS")

    def test_update_relation(self):
        print("test_update_relation:","NOT IMPLEMENTED")
        return #todo AE: fix this test
    
    def test_has_relation(self):
        print("test_has_relation:","NOT IMPLEMENTED")
        return #todo AE: fix this test
    
    def test_generate_policy(self):
        node = SimulaeNode(given_id="node", nodetype=POI)
        policy = node.generate_policy()
        self.assertIsInstance(policy, dict)
        self.assertGreater(len(policy), 0)
        print("test_generate_policy:", "PASS")

    def test_generate_personality(self):
        node = SimulaeNode(given_id="node", nodetype=POI)
        personality = node.generate_personality()
        print("Personality:")
        pprint(personality)
        self.assertIsInstance(personality, dict)
        self.assertGreater(len(personality), 0)
        print("test_generate_personality:", "PASS")

    def test_get_policy_disposition(self):
        print("test_get_policy_disposition:","NOT IMPLEMENTED")
        return #todo AE: fix this test
        
    def test_policy_diff(self):
        print("test_policy_diff:","NOT IMPLEMENTED")
        return #todo AE: fix this test
        
    def test_get_policy_index(self):
        node = SimulaeNode(given_id="node", nodetype=POI)
        index = node.get_policy_index("Economy", "Indifferent")
        self.assertEqual(index, 3)
        print("test_get_policy_index:", "PASS")

    def test_to_JSON(self):
        node = SimulaeNode(given_id="node", nodetype=POI)
        json_data = node.toJSON()
        self.assertIsInstance(json_data, dict)
        print("test_to_JSON:", "PASS")


class Test_generate_simulae_node(unittest.TestCase):
    def test_generate_simulae_node(self):

        for nt in ALL_NODE_TYPES:
            expected = SimulaeNode(nodetype=nt)

            generated = generate_simulae_node(nt)

            self.assertIsInstance(generated, SimulaeNode)

            self.assertIsInstance(generated.ID, str)

            if nt in SOCIAL_NODE_TYPES:
                self.assertIn(POLICY, generated.References)
                self.assertIsNotNone(generated.References[POLICY])

    def test_generate_simulae_node_with_name(self):

        nodename = "NODE"

        expected = SimulaeNode(given_id=nodename)

        generated = generate_simulae_node(OBJ, node_name=nodename)

        self.assertEqual(generated.ID, expected.ID)

