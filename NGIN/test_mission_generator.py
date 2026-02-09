import unittest
from unittest.mock import patch, MagicMock
from .SimulaeCampaignGenerator import NGIN
from .SimulaeNode import SimulaeNode, OBJ
from .NGIN_utils.ngin_utils import load_json_from_file

class Test_NGIN(unittest.TestCase):

    def setUp(self):
        self.mission_struct = load_json_from_file("NGIN/NGIN_config/story_struct.json")
        self.settings = load_json_from_file("NGIN/NGIN_config/ngin_settings.json")
        self.ngin = NGIN(self.mission_struct, self.settings, generate=False)

    def test_generate_element(self):
        element = self.ngin.generate_element(OBJ)
        self.assertIsInstance(element, SimulaeNode)
        self.assertIsNotNone(element.ID)
        self.assertEqual(element.Nodetype, OBJ)

        print("test_generate_element:", "PASS")

    # def test_generate_state(self):
    #     state = self.ngin.generate_state(3)
    #     self.assertEqual(len(state), 3)
    #     for element in state:
    #         self.assertIsInstance(element, SimulaeNode)

    ''' AE Disabled UserChoice test -> stuck in loop
    @patch('builtins.input', side_effect=['0'])
    def test_user_choice_literal(self, mock_input):
        options = ['yes', 'no']
        choice = NGIN.user_choice(options, literal=True)
        self.assertEqual(choice, 'yes')
    '''
        
    # @patch('builtins.input', side_effect=['1'])
    # def test_user_choice_index(self, mock_input):
    #     options = ['yes', 'no']
    #     choice = NGIN.user_choice(options, literal=False)
    #     self.assertEqual(choice, 'no')

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