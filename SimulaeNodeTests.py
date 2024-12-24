import unittest

from SimulaeNode import *


class Test_SimulaeNode(unittest.TestCase):

    def test_init(self):
        pass

    def test_summary(self):
        pass

    def test_str_(self):
        pass

    def test_add_adjacent_location(self):
        pass

    def test_get_adjacent_locations(self):
        pass

    def test_knows_about(self):
        pass

    def test_get_reference(self):
        pass

    def test_add_reference(self):
        pass

    def test_get_attribute(self):
        pass

    def test_update_relation(self):
        pass

    def test_has_relation(self):
        pass

    def test_generate_policy(self):
        # verify each factor is included with a value
        pass

    def test_get_policy_disposition(self):
        pass

    def test_policy_diff(self):
        pass

    def test_get_policy_index(self):
        pass

    def test_to_JSON(self):
        pass










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

    def test_generate_simulae_node_with_faction(self):

        nodename = "NODE"

        faction = SimulaeNode(given_id="FACTION",nodetype=FAC)

        generated = generate_simulae_node(POI, node_name=nodename, faction=faction)

        self.assertEqual(generated.references[FAC], faction.id)


if __name__ == '__main__':
    unittest.main()