import unittest

from SimulaeNode import *

class Test_SimulaeNode(unittest.TestCase):

    def test_init_POI(self):

        node = SimulaeNode(nodetype=POI)

        self.assertIsNotNone(node.id)
        self.assertEqual(node.nodetype, POI)

        self.assertEqual(node.status, Status.ALIVE)

        self.assertIsNotNone(node.references)
        
        references_keys = node.references.keys()
        self.assertIn(NAME, references_keys)
        self.assertIn(POLICY, references_keys)
        self.assertIsNotNone(node.references[POLICY])
        self.assertIsNotNone(node.attributes)

        self.assertIsNotNone(node.relations)
        for relation, relatives in node.relations.items():
            self.assertIn(relation, RELATIONS)
            relations_keys = relatives.keys()
            self.assertEqual(list(relations_keys).sort(), NODETYPES.sort())

            for nt, items in relatives.items():
                self.assertEqual(items, {})

    def test_init_OBJ(self):

        node = SimulaeNode()

        self.assertIsNotNone(node.id)
        self.assertEqual(node.nodetype, OBJ)

        self.assertEqual(node.status, Status.ALIVE)

        self.assertIsNotNone(node.references)
        
        references_keys = node.references.keys()
        self.assertIn(NAME, references_keys)
        self.assertIsNotNone(node.attributes)

        self.assertIsNotNone(node.relations)
        for relation, relatives in node.relations.items():
            self.assertIn(relation, RELATIONS)
            relations_keys = relatives.keys()
            self.assertEqual(list(relations_keys).sort(), NODETYPES.sort())

            for nt, items in relatives.items():
                self.assertEqual(items, {})

    def test_summary(self):
        return #todo AE: fix this test
        
    def test_str_(self):
        node = SimulaeNode(given_id="test_node", nodetype=POI, references={NAME: "Test Node"})

        self.assertNotEqual(str(node), "")

    def test_add_adjacent_location(self):
        return #todo AE: fix this test

    def test_get_adjacent_locations(self):
        node = SimulaeNode(given_id="node", nodetype=LOC, references={ADJACENT: ["loc1", "loc2"]})
        adjacents = node.get_adjacent_locations()
        self.assertIn("loc1", adjacents)
        self.assertIn("loc2", adjacents)

    def test_knows_about(self):
        return #todo AE: fix this test

    def test_get_reference(self):
        node = SimulaeNode(given_id="node", references={NAME: "Test Node"})
        self.assertEqual(node.get_reference(NAME), "Test Node")

    def test_add_reference(self):
        return #todo AE: fix this test

    def test_get_attribute(self):
        node = SimulaeNode(given_id="node", attributes={"interactions": 5})
        self.assertEqual(node.get_attribute("interactions"), 5)

    def test_update_relation(self):
        return #todo AE: fix this test
    def test_has_relation(self):
        return #todo AE: fix this test
    

    def test_generate_policy(self):
        node = SimulaeNode(given_id="node", nodetype=POI)
        policy = node.generate_policy()
        self.assertIsInstance(policy, dict)
        self.assertGreater(len(policy), 0)

    def test_get_policy_disposition(self):
        return #todo AE: fix this test
        
    def test_policy_diff(self):
        return #todo AE: fix this test
        
    def test_get_policy_index(self):
        node = SimulaeNode(given_id="node", nodetype=POI)
        index = node.get_policy_index("Economy", "Indifferent")
        self.assertEqual(index, 2)

    def test_to_JSON(self):
        node = SimulaeNode(given_id="node", nodetype=POI)
        json_data = node.toJSON()
        self.assertIsInstance(json_data, dict)


class Test_generate_simulae_node(unittest.TestCase):
    def test_generate_simulae_node(self):

        for nt in ALL_NODE_TYPES:
            expected = SimulaeNode(nodetype=nt)

            generated = generate_simulae_node(nt)

            self.assertIsInstance(generated, SimulaeNode)

            self.assertIsInstance(generated.id, uuid.UUID)

            if nt in SOCIAL_NODE_TYPES:
                self.assertIn(POLICY, generated.references)
                self.assertIsNotNone(generated.references[POLICY])

    def test_generate_simulae_node_with_name(self):

        nodename = "NODE"

        expected = SimulaeNode(given_id=nodename)

        generated = generate_simulae_node(OBJ, node_name=nodename)

        self.assertEqual(generated.id, expected.id)

