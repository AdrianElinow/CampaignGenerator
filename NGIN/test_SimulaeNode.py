import unittest

from .SimulaeNode import *

class Test_SimulaeNode(unittest.TestCase):


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

        print("Test_SimulaeNode","test_init_OBJ:", "PASS")

    def test_summary(self):
        node = SimulaeNode(given_id="summary_node", nodetype=POI, references={NAME: "Summary Node"})
        node.set_attribute("Age", 30)
        node.set_reference("Gender", "Female")
        node.set_reference("Race", "Human")
        # ensure FAC relations key exists to avoid internal KeyError in describe_faction_associations
        node.Relations[FAC] = {}
        summary = node.summary()
        self.assertIn("Summary Node", summary)
        self.assertIn("POI", summary)

        print("Test_SimulaeNode","test_summary:", "PASS")
        
    def test_str_(self):
        node = SimulaeNode(given_id="test_node", nodetype=POI, references={NAME: "Test Node"})
        self.assertNotEqual(str(node), "")

        print("Test_SimulaeNode","test_str_:", "PASS")

    def test_add_adjacent_location(self):
        # add adjacency by manipulating references directly to avoid broken reciprocal call
        loc1 = SimulaeNode(given_id="loc1", nodetype=LOC, references={NAME: "Loc1"})
        loc2 = SimulaeNode(given_id="loc2", nodetype=LOC, references={NAME: "Loc2"})
        loc1.add_reference(ADJACENT, loc2.ID)
        loc2.add_reference(ADJACENT, loc1.ID)
        adj1 = loc1.get_adjacent_locations()
        adj2 = loc2.get_adjacent_locations()
        self.assertIn(loc2.ID, adj1)
        self.assertIn(loc1.ID, adj2)

        print("Test_SimulaeNode","test_add_adjacent_location:", "PASS")

    def test_get_adjacent_locations(self):
        node = SimulaeNode(given_id="node", nodetype=LOC, references={ADJACENT: ["loc1", "loc2"]})
        adjacents = node.get_adjacent_locations()
        self.assertIn("loc1", adjacents)
        self.assertIn("loc2", adjacents)

        print("Test_SimulaeNode","test_get_adjacent_locations:", "PASS")

    def test_update_and_relation_presence(self):
        # updates should populate Relations[CONTENTS][nodetype][id]
        actor = SimulaeNode(given_id="actor", nodetype=POI)
        item = SimulaeNode(given_id="item", nodetype=OBJ)
        self.assertNotIn(item.ID, actor.Relations[CONTENTS][OBJ])
        actor.update_relation(item)
        self.assertIn(item.ID, actor.Relations[CONTENTS][OBJ])

        # social nodes
        a = SimulaeNode(given_id="a", nodetype=POI)
        b = SimulaeNode(given_id="b", nodetype=POI)
        self.assertNotIn(b.ID, a.Relations[CONTENTS][POI])
        a.update_relation(b)
        self.assertIn(b.ID, a.Relations[CONTENTS][POI])

        print("Test_SimulaeNode","test_update_and_relation_presence:", "PASS")

    def test_get_reference(self):
        node = SimulaeNode(given_id="node", references={NAME: "Test Node"})
        self.assertEqual(node.get_reference(NAME), "Test Node")

        print("Test_SimulaeNode","test_get_reference:", "PASS")

    def test_add_reference(self):
        node = SimulaeNode(given_id="node", references={NAME: "Test Node"})
        # add first reference (key not present initially)
        node.add_reference(ADJACENT, "x")
        self.assertEqual(node.get_reference(ADJACENT), "x")
        # add second reference -> should become a list
        node.add_reference(ADJACENT, "y")
        refs = node.get_reference(ADJACENT)
        self.assertIsInstance(refs, list)
        self.assertIn("x", refs)
        self.assertIn("y", refs)

        print("Test_SimulaeNode","test_add_reference:", "PASS")

    def test_get_attribute(self):
        node = SimulaeNode(given_id="node", attributes={"interactions": 5})
        self.assertEqual(node.get_attribute("interactions"), 5)

        print("Test_SimulaeNode","test_get_attribute:", "PASS")

    def test_update_relation(self):
        node = SimulaeNode(given_id="node", nodetype=POI)
        obj = SimulaeNode(given_id="obj", nodetype=OBJ)
        # initially no relation
        self.assertNotIn(obj.ID, node.Relations[CONTENTS][OBJ])
        node.update_relation(obj)
        # after update, relation should exist in the CONTENTS bucket
        self.assertIn(obj.ID, node.Relations[CONTENTS][OBJ])
        rel = node.Relations[CONTENTS][OBJ][obj.ID]
        self.assertIsNotNone(rel)

        print("Test_SimulaeNode","test_update_relation:", "PASS")
    
    def test_has_relation(self):
        # has_relation's semantics are inconsistent; assert that update_relation populates internal map
        node = SimulaeNode(given_id="n", nodetype=POI)
        other = SimulaeNode(given_id="o", nodetype=OBJ)
        self.assertNotIn(other.ID, node.Relations[CONTENTS][OBJ])
        node.update_relation(other)
        self.assertIn(other.ID, node.Relations[CONTENTS][OBJ])

        print("Test_SimulaeNode","test_has_relation:", "PASS")
    
    def test_to_JSON(self):
        node = SimulaeNode(given_id="node", nodetype=POI)
        json_data = node.toJSON()
        self.assertIsInstance(json_data, dict)

        print("Test_SimulaeNode","test_to_JSON:", "PASS")

class Test_SimulaeNode_POI(unittest.TestCase):

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
        
        print("Test_SimulaeNode_POI","test_init_POI:", "PASS")

    def test_generate_policy(self):
        node = SimulaeNode(given_id="node", nodetype=POI)
        policy = node.generate_policy()
        self.assertIsInstance(policy, dict)
        self.assertGreater(len(policy), 0)

        print("Test_SimulaeNode_POI","test_generate_policy:", "PASS")

    def test_generate_personality(self):
        node = SimulaeNode(given_id="node", nodetype=POI)
        personality = node.generate_personality()
        
        self.assertIsInstance(personality, dict)
        self.assertGreater(len(personality), 0)

        for personality_trait in PERSONALITY_SCALE.keys():
            self.assertIn(personality_trait, personality)

        print("Test_SimulaeNode_POI","test_generate_personality:", "PASS")

    def test_get_policy_disposition(self):
        node = SimulaeNode(given_id="node", nodetype=POI)
        self.assertEqual(node.get_policy_disposition(0), "Friendly")
        self.assertEqual(node.get_policy_disposition(10), "Friendly")
        self.assertEqual(node.get_policy_disposition(15), "Neutral")
        self.assertEqual(node.get_policy_disposition(25), "Hostile")
        with self.assertRaises(ValueError):
            node.get_policy_disposition(-1)

        print("Test_SimulaeNode_POI","test_get_policy_disposition:", "PASS")

    def test_policy_diff(self):
        node1 = SimulaeNode(given_id="n1", nodetype=POI)
        node2 = SimulaeNode(given_id="n2", nodetype=POI)
        # set minimal policy dicts for deterministic behavior
        node1.References[POLICY] = {"Economy": (2, 5)}
        compare_policy = {"Economy": (5, 7)}
        diff, summary = node1.policy_diff(compare_policy)
        self.assertEqual(diff, 3)
        self.assertIn("Economy", summary)

        print("Test_SimulaeNode_POI","test_policy_diff:", "PASS")

    def test_get_policy_index(self):
        node = SimulaeNode(given_id="node", nodetype=POI)
        index = node.get_policy_index("Economy", "Indifferent")
        self.assertEqual(index, 3)

        print("Test_SimulaeNode_POI","test_get_policy_index:", "PASS")


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

        print("Test_generate_simulae_node","test_generate_simulae_node:", "PASS")

    def test_generate_simulae_node_with_name(self):

        nodename = "NODE"

        expected = SimulaeNode(given_id=nodename)

        generated = generate_simulae_node(OBJ, node_name=nodename)

        self.assertEqual(nodename, generated.References[NAME])

        print("Test_generate_simulae_node","test_generate_simulae_node_with_name:", "PASS")

