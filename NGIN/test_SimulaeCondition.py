import unittest

from .SimulaeCondition import SimulaeCondition
from .SimulaeConstants import ATTRIBUTES, CND, NAME, OBJ, POI, REFERENCES
from .SimulaeNode import SimulaeNode


class TestSimulaeConditionCore(unittest.TestCase):
    def test_init_sets_identity_and_conditions(self):
        conditions = [{"op": ">=", "left": {"property": ATTRIBUTES, "key": "Mana"}, "right": {"value": 30}}]
        cond = SimulaeCondition(
            id="cond-1",
            name="Mana Gate",
            conditions=conditions,
        )

        self.assertEqual(cond.ID, "cond-1")
        self.assertEqual(cond.Nodetype, CND)
        self.assertEqual(cond.get_reference(NAME), "Mana Gate")
        self.assertEqual(cond.Conditions, conditions)

    def test_satisfies_conditions_false_when_node_missing(self):
        cond = SimulaeCondition(
            id="cond-2",
            name="Missing Node",
            conditions=[{"op": "==", "left": {"value": 1}, "right": {"value": 1}}],
        )
        self.assertFalse(cond.satisfies_conditions(None))

    def test_satisfies_conditions_false_when_no_conditions(self):
        node = SimulaeNode(nodetype=POI, references={NAME: "Caster"})
        cond = SimulaeCondition(
            id="cond-3",
            name="No Conditions",
            conditions=[],
        )
        self.assertFalse(cond.satisfies_conditions(node))


@unittest.skip("Planned SimulaeCondition evaluator behavior from Simulae Condition/Abilities docs.")
class TestSimulaeConditionPlannedBehavior(unittest.TestCase):
    def setUp(self):
        self.source = SimulaeNode(
            given_id="source-node",
            nodetype=POI,
            references={NAME: "Caster"},
            attributes={"Mana": 45, "ArmorPenetration": 15},
        )
        self.target = SimulaeNode(
            given_id="target-node",
            nodetype=POI,
            references={NAME: "Target"},
            attributes={"Armor": 10},
        )
        self.source.set_relation(self.target, "Contents")

    def test_attribute_comparison_condition(self):
        cond = SimulaeCondition(
            id="cond-doc-1",
            name="Has Mana",
            conditions=[
                {
                    "left": {"bind": "source", "nodetype": POI, "property": ATTRIBUTES, "key": "Mana", "subkey": None},
                    "op": ">=",
                    "right": {"value": 30},
                }
            ],
        )
        self.assertTrue(cond.satisfies_conditions(self.source))

    def test_cross_binding_comparison_condition(self):
        cond = SimulaeCondition(
            id="cond-doc-2",
            name="Penetration Beats Armor",
            conditions=[
                {
                    "left": {
                        "bind": "target",
                        "nodetype": POI,
                        "property": ATTRIBUTES,
                        "key": "Armor",
                        "subkey": None,
                    },
                    "op": "<",
                    "right": {
                        "bind": "source",
                        "nodetype": POI,
                        "property": ATTRIBUTES,
                        "key": "ArmorPenetration",
                        "subkey": None,
                    },
                }
            ],
        )
        self.assertTrue(cond.satisfies_conditions(self.source))

    def test_collection_filter_condition(self):
        wand = SimulaeNode(given_id="wand-1", nodetype=OBJ, references={NAME: "Wand"})
        self.source.set_relation(wand, "Contents")

        cond = SimulaeCondition(
            id="cond-doc-3",
            name="Has Wand",
            conditions=[
                {
                    "left": {
                        "bind": "actor",
                        "component": "Relations",
                        "relation_type": "Contents",
                        "nodetype": OBJ,
                        "filter": {
                            "component": REFERENCES,
                            "keys": [NAME],
                            "op": "eq",
                            "value": "Wand",
                        },
                    },
                    "op": "count_gte",
                    "right": {"value": 1},
                }
            ],
        )
        self.assertTrue(cond.satisfies_conditions(self.source))


if __name__ == "__main__":
    unittest.main()
