import unittest

from NGIN.SimulaeNode import *



class Test_SimulaeNode(unittest.TestCase):

    def test_init_POI(self):

        node = SimulaeNode(nodetype=POI)

        self.assertIsNotNone(node.id)
        self.assertEqual(node.nodetype, POI)

        self.assertEqual(node.status, Status.ALIVE)

        self.assertIsNotNone(node.references)
        
        references_keys = node.references.keys()
        self.assertIn(NAME, references_keys)
        self.assertIn(FAC, references_keys)
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
        self.assertIn(FAC, references_keys)
        self.assertIsNotNone(node.attributes)

        self.assertIsNotNone(node.relations)
        for relation, relatives in node.relations.items():
            self.assertIn(relation, RELATIONS)
            relations_keys = relatives.keys()
            self.assertEqual(list(relations_keys).sort(), NODETYPES.sort())

            for nt, items in relatives.items():
                self.assertEqual(items, {})

    def test_summary(self):
        node = SimulaeNode(given_id="test_node", nodetype=POI, references={NAME: "Test Node", FAC: "Test Faction"})
        summary = node.summary()
        self.assertIn("POI", summary)
        self.assertIn("Test Node", summary)
        self.assertIn("affiliated with Test Faction", summary)

    def test_str_(self):
        node = SimulaeNode(given_id="test_node", nodetype=POI, references={NAME: "Test Node"})
        self.assertEqual(str(node), node.summary())

    def test_add_adjacent_location(self):
        return #todo AE: fix this test

        node1 = SimulaeNode(given_id="node1", nodetype=LOC)
        node2 = SimulaeNode(given_id="node2", nodetype=LOC)
        node1.add_adjacent_location(node2)
        self.assertIn("node2", node1.get_adjacent_locations())
        self.assertIn("node1", node2.get_adjacent_locations())

    def test_get_adjacent_locations(self):
        node = SimulaeNode(given_id="node", nodetype=LOC, references={ADJACENT: ["loc1", "loc2"]})
        adjacents = node.get_adjacent_locations()
        self.assertIn("loc1", adjacents)
        self.assertIn("loc2", adjacents)

    def test_knows_about(self):
        return #todo AE: fix this test
        node1 = SimulaeNode(given_id="node1", nodetype=POI)
        node2 = SimulaeNode(given_id="node2", nodetype=OBJ)
        node1.update_relation(node2)
        self.assertTrue(node1.knows_about(node2))

    def test_get_reference(self):
        node = SimulaeNode(given_id="node", references={NAME: "Test Node"})
        self.assertEqual(node.get_reference(NAME), "Test Node")

    def test_add_reference(self):
        return #todo AE: fix this test
        node = SimulaeNode(given_id="node")
        node.add_reference(NAME, "Test Node")
        self.assertEqual(node.get_reference(NAME), "Test Node")

    def test_get_attribute(self):
        node = SimulaeNode(given_id="node", attributes={"interactions": 5})
        self.assertEqual(node.get_attribute("interactions"), 5)

    def test_update_relation(self):
        return #todo AE: fix this test
        node1 = SimulaeNode(given_id="node1", nodetype=POI)
        node2 = SimulaeNode(given_id="node2", nodetype=OBJ)
        node1.update_relation(node2)
        self.assertIsNotNone(node1.get_relation("node2", OBJ))

    def test_has_relation(self):
        return #todo AE: fix this test
    
        node1 = SimulaeNode(given_id="node1", nodetype=POI)
        node2 = SimulaeNode(given_id="node2", nodetype=OBJ)
        node1.relations[OBJ]["node2"] = {}
        self.assertTrue(node1.has_relation("node2", OBJ))

    def test_generate_policy(self):
        node = SimulaeNode(given_id="node", nodetype=POI)
        policy = node.generate_policy()
        self.assertIsInstance(policy, dict)
        self.assertGreater(len(policy), 0)

    def test_get_policy_disposition(self):
        return #todo AE: fix this test
        node = SimulaeNode(given_id="node", nodetype=POI)
        disposition = node.get_policy_disposition(5)
        self.assertEqual(disposition, "Friendly")

    def test_policy_diff(self):
        return #todo AE: fix this test
        
        node1 = SimulaeNode(given_id="node1", nodetype=POI, references={POLICY: {"Economy": ["Indifferent", 0.5], "Health": ["Supportive", 0.7]}})
        node2 = SimulaeNode(given_id="node2", nodetype=POI, references={POLICY: {"Economy": ["Opposed", 0.5], "Health": ["Neutral", 0.3]}})
        diff, summary = node1.policy_diff(node2.references[POLICY])
        self.assertGreater(diff, 0)
        self.assertIn("Economy", summary)

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

            generated = generate_random_simulae_node(nt)

            self.assertIsInstance(generated, SimulaeNode)

            self.assertIsInstance(generated.id, uuid.UUID)

            if nt in SOCIAL_NODE_TYPES:
                self.assertIn(POLICY, generated.references)
                self.assertIsNotNone(generated.references[POLICY])

    def test_generate_simulae_node_with_name(self):

        nodename = "NODE"

        expected = SimulaeNode(given_id=nodename)

        generated = generate_random_simulae_node(OBJ, node_name=nodename)

        self.assertEqual(generated.id, expected.id)

    def test_generate_simulae_node_with_faction(self):

        nodename = "NODE"

        faction = SimulaeNode(given_id="FACTION",nodetype=FAC)

        generated = generate_random_simulae_node(POI, node_name=nodename, faction=faction)

        self.assertEqual(generated.references[FAC], faction.id)
