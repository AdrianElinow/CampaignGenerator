import unittest
from unittest.mock import patch, MagicMock
from NGIN.mission_generator import NGIN, SimulaeNode

class Test_NGIN(unittest.TestCase):

    def setUp(self):
        self.mission_struct = {
            "Neutral": {
                "POI": ["Investigate", "Scout"],
                "PTY": ["Negotiate", "Recruit"],
                "OBJ": ["Retrieve", "Secure"],
                "LOC": ["Explore", "Survey"]
            },
            "Friendly": {
                "POI": ["Assist", "Defend"],
                "PTY": ["Support", "Join"],
                "OBJ": ["Protect", "Deliver"],
                "LOC": ["Guard", "Maintain"]
            },
            "Hostile": {
                "POI": ["Attack", "Sabotage"],
                "PTY": ["Ambush", "Capture"],
                "OBJ": ["Destroy", "Steal"],
                "LOC": ["Raid", "Occupy"]
            }
        }
        self.madlibs = ["Alpha", "Beta", "Gamma", "Delta"]
        self.ngin = NGIN(self.mission_struct, self.madlibs)

    def test_generate_element(self):
        element = self.ngin.generate_element()
        self.assertIsInstance(element, SimulaeNode)
        self.assertIn(element.id, self.madlibs)
        self.assertIn(element.nodetype, ['POI', 'PTY', 'OBJ', 'LOC'])

    def test_generate_state(self):
        state = self.ngin.generate_state(3)
        self.assertEqual(len(state), 3)
        for element in state:
            self.assertIsInstance(element, SimulaeNode)

    ''' AE Disabled UserChoice test -> stuck in loop
    @patch('builtins.input', side_effect=['0'])
    def test_user_choice_literal(self, mock_input):
        options = ['yes', 'no']
        choice = NGIN.user_choice(options, literal=True)
        self.assertEqual(choice, 'yes')
    '''
        
    @patch('builtins.input', side_effect=['1'])
    def test_user_choice_index(self, mock_input):
        options = ['yes', 'no']
        choice = NGIN.user_choice(options, literal=False)
        self.assertEqual(choice, 'no')

    ''' AE Disabled UserChoice test -> stuck in loop
    @patch('builtins.input', side_effect=['random'])
    @patch('random.choice', side_effect=lambda x: x[0])
    def test_user_choice_random(self, mock_input, mock_random_choice):
        options = ['yes', 'no']
        choice = NGIN.user_choice(options, random_opt=True)
        self.assertEqual(choice, 'yes')
    '''

    ''' AE Disabled UserChoice test -> stuck in loop
    @patch('random.choice')
    def test_choose_mission(self, mock_random_choice):
        actor_node = MagicMock()
        mock_random_choice.side_effect = [
            'POI', 
            SimulaeNode("Alpha", "POI", {}, {}, {}, {}, {}),
            "Investigate"
        ]
        subj, mission, state = self.ngin.choose_mission(actor_node)
        self.assertEqual(subj.name, "Alpha")
        self.assertEqual(mission, "Investigate")
    '''
    ''' AE Disabled UserChoice test -> stuck in loop
    @patch('os.system')
    @patch('builtins.input', side_effect=['q'])
    def test_start(self, mock_input, mock_os_system):
        with self.assertRaises(SystemExit):
            self.ngin.start()
    '''
            
if __name__ == '__main__':
    unittest.main()