import unittest
from NGIN_AI import NGIN_Simulae_Actor, generate_individual

class Test_NGINAI(unittest.TestCase):

    def setUp(self):
        self.actor = NGIN_Simulae_Actor(generate_individual())

    def test_initial_attributes(self):
        self.assertIsNotNone(self.actor.SimulaeNode)
        self.assertEqual(self.actor.inventory, {})
        self.assertTrue(self.actor.priorities.empty())

    def test_problem_solve_no_priorities(self):
        actions = self.actor.problem_solve()
        self.assertEqual(actions, [])

    def test_problem_solve_with_hunger(self):
        self.actor.SimulaeNode.set_attribute('hunger', 10)
        actions = self.actor.problem_solve()
        self.assertIn(('use', 'food'), actions)

    def test_problem_solve_with_thirst(self):
        self.actor.SimulaeNode.set_attribute('thirst', 20)
        actions = self.actor.problem_solve()
        self.assertIn(('use', 'drink'), actions)

    def test_problem_solve_with_exhaustion(self):
        self.actor.SimulaeNode.set_attribute('exhaustion', 70)
        actions = self.actor.problem_solve()
        self.assertIn(('use', 'sleep'), actions)

    def test_problem_solve_with_socialization(self):
        self.actor.SimulaeNode.set_attribute('social', 20)
        actions = self.actor.problem_solve()
        self.assertIn(('use', 'socialize'), actions)

    def test_prioritize(self):
        self.actor.SimulaeNode.set_attribute('hunger', 10)
        self.actor.SimulaeNode.set_attribute('thirst', 20)
        self.actor.SimulaeNode.set_attribute('exhaustion', 70)
        self.actor.SimulaeNode.set_attribute('social', 20)
        priorities = self.actor.prioritize()
        self.assertFalse(priorities.empty())

    def test_has(self):
        self.actor.inventory = {'food': 1}
        self.assertTrue(self.actor.has('food'))
        self.assertFalse(self.actor.has('drink'))

    def test_consume(self):
        self.actor.inventory = {'food': 1}
        actions = self.actor.consume('food')
        self.assertEqual(actions, ('use', 'food'))

if __name__ == '__main__':
    unittest.main()