import unittest
from .NGIN_AI import NGIN_Simulae_Actor, generate_individual, generate_food_item, generate_drink_item

class Test_NGINAI(unittest.TestCase):

    def setUp(self):
        self.actor = NGIN_Simulae_Actor(generate_individual())
        self.actor.inventory["OBJ"] = {}

    def test_initial_attributes(self):
        self.assertIsNotNone(self.actor.SimulaeNode)
        self.assertIsNotNone(self.actor.inventory)
        self.assertTrue(self.actor.priorities.empty())

    def test_problem_solve_no_priorities(self):
        actions = self.actor.problem_solve()
        self.assertEqual(actions, [])

    def test_problem_solve_hunger_with_food_in_inventory(self):
        self.actor.SimulaeNode.set_attribute('hunger', 10)

        SN_food = generate_food_item()
        self.actor.inventory[SN_food.nodetype][SN_food.id] = SN_food

        actions = self.actor.problem_solve()
        self.assertIn(('use', SN_food), actions)

    def test_problem_solve_thirst_with_drink_in_inventory(self):
        self.actor.SimulaeNode.set_attribute('thirst', 20)

        SN_drink = generate_drink_item()

        self.actor.inventory[SN_drink.nodetype][SN_drink.id] = SN_drink
        
        actions = self.actor.problem_solve()
        self.assertIn(('use', SN_drink), actions)

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
        food = generate_food_item()

        self.actor.inventory[food.nodetype][food.id] = food
        self.assertTrue(self.actor.has_vague('edible', food.nodetype))
        self.assertFalse(self.actor.has_vague('drinkable', food.nodetype))

    def test_consume(self):
        drink = generate_drink_item()
        self.actor.inventory[drink.nodetype][drink.id] = drink

        food = generate_food_item()
        self.actor.inventory[food.nodetype][food.id] = food

        actions = self.actor.consume('drinkable')
        self.assertIn(('use', drink), actions)

        actions = self.actor.consume('edible')
        self.assertIn(('use', food),actions)

if __name__ == '__main__':
    unittest.main()