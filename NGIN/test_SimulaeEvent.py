import unittest

from .SimulaeConstants import EVT, OBS, SRC, TGT
from .SimulaeEvent import SimulaeEvent
from .SimulaeNode import SimulaeNode


class TestSimulaeEventCore(unittest.TestCase):
    def _build_event(self):
        return SimulaeEvent(
            id="evt-1",
            event_class="social",
            event_type="Inform",
            event_subtype="Claim",
            start_timestamp="100",
            end_timestamp="101",
            sources=["source-a"],
            targets=["target-a"],
            observers=["observer-a"],
            effects=[{"path": "Attributes.Health", "op": "add", "value": -1}],
        )

    def test_init_sets_nodetype_and_references(self):
        event = self._build_event()

        self.assertEqual(event.Nodetype, EVT)
        self.assertEqual(event.get_reference("event_class"), "social")
        self.assertEqual(event.get_reference("event_type"), "Inform")
        self.assertEqual(event.get_reference("event_subtype"), "Claim")
        self.assertEqual(event.get_reference("start_timestamp"), "100")
        self.assertEqual(event.get_reference("end_timestamp"), "101")
        self.assertIsInstance(event.get_reference("created_timestamp"), str)

    def test_init_creates_relation_channels(self):
        event = self._build_event()

        self.assertIn(SRC, event.Relations)
        self.assertIn(TGT, event.Relations)
        self.assertIn(OBS, event.Relations)
        self.assertEqual(event.Relations[SRC], {})
        self.assertEqual(event.Relations[TGT], {})
        self.assertEqual(event.Relations[OBS], {})

    def test_effects_assigned(self):
        event = self._build_event()
        self.assertEqual(len(event.Effects), 1)
        self.assertEqual(event.Effects[0]["op"], "add")


@unittest.skip("Planned SimulaeEvent behavior from Simulae Event and Event System docs.")
class TestSimulaeEventPlannedBehavior(unittest.TestCase):
    def setUp(self):
        self.source = SimulaeNode(given_id="src-1")
        self.target = SimulaeNode(given_id="tgt-1")
        self.observer = SimulaeNode(given_id="obs-1")

    def test_constructor_materializes_sources_targets_observers(self):
        event = SimulaeEvent(
            id="evt-planned-1",
            event_class="physical",
            event_type="Attack",
            event_subtype="Strike",
            start_timestamp="200",
            end_timestamp="201",
            sources=[self.source.ID],
            targets=[self.target.ID],
            observers=[self.observer.ID],
            effects=[],
        )

        # Planned: constructor should store provided ids into relation channels.
        self.assertIn(self.source.ID, event.Relations[SRC])
        self.assertIn(self.target.ID, event.Relations[TGT])
        self.assertIn(self.observer.ID, event.Relations[OBS])

    def test_start_timestamp_defaults_to_created_timestamp(self):
        event = SimulaeEvent(
            id="evt-planned-2",
            event_class="system",
            event_type="Heartbeat",
            event_subtype="Tick",
            start_timestamp=None,
            end_timestamp=None,
            sources=[],
            targets=[],
            observers=[],
            effects=[],
        )

        self.assertEqual(
            event.get_reference("start_timestamp"),
            event.get_reference("created_timestamp"),
        )

    def test_membership_helpers_use_event_participant_sets(self):
        event = SimulaeEvent(
            id="evt-planned-3",
            event_class="social",
            event_type="Inform",
            event_subtype="Whisper",
            start_timestamp="300",
            end_timestamp="301",
            sources=[],
            targets=[],
            observers=[],
            effects=[],
        )

        self.assertTrue(event.add_source("src-2"))
        self.assertTrue(event.add_target("tgt-2"))
        self.assertTrue(event.add_observer("obs-2"))
        self.assertTrue(event.was_perpetrated_by("src-2"))
        self.assertTrue(event.was_inflicted_upon("tgt-2"))
        self.assertTrue(event.was_observed_by("obs-2"))


if __name__ == "__main__":
    unittest.main()
