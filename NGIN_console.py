import json, sys, os, random
from pprint import pprint

from SimulaeNode import *

class NGIN_console():

    def __init__(self, mission_struct, settings, madlibs, save_file=None ):
        self.mission_struct = mission_struct
        self.madlibs = madlibs
        self.settings = settings
        self.state = SimulaeNode(
                        "state",        # id
                        "",             # nodetype
                        {},
                        {},
                        {
                            "FAC":{},
                            "PTY":{},
                            "POI":{},
                            "OBJ":{},
                            "LOC":{}
                        },
                        {},
                        {}
                    )

        if save_file:
            self.load_save_data(save_file)

    def validate_state(self):
        print('validate_state(..)')

    def display_state(self, perceiver):
        print('display_state(..)')

        ''' Display state available to 'perceiver'
        '''

    def resolve_mission(self, mission, subject):
        print('resolve_mission( mission: [{0}], subject: [{1}] )'.format( mission, subject ) )

        ''' perform immediate node state changes 
                ex: kill enemy -> remove enemy node, gain xp/money/reward, etc
                 recruit neutral -> add to faction, gain rewards, etc
        '''

        ''' calculate ripple effect 
                gain intel from node?
                    learn about new enemy nodes? 


        ''' 

    def choose_mission(self):
        print('choose_mission(..)')

        # compile list of available interactable nodes

        # pick from list

        return subject, mission




    def start(self):
        ''' Iterates through the game state generating missions based on
                available nodes in the state.
        '''

        input('<Press "ENTER" to START>')

        while True:

            os.system('clear') # clear screen

            self.validate_state()

            self.display_state()

            subject, mission = self.choose_mission()

            self.resolve_mission(mission, subject)

            cmd = input('continue [enter] / [q]uit ?> ')
            if cmd in ['q','quit']:
                sys.exit(0) 

    def user_choice( self, user_options, literal=False, random_opt=False ):
        ''' Present user with available options, and allow them to pick
                an option to proceed. 

            literal : does the user need to type out the option explicitly?
                True -> user must enter the explicit option as typed.
                False -> user will instead enter the option's presented index
            random_opt : allow the user to select 'random' which will randomly
                select an option instead?
        '''

        choice = None
        chosen = None

        if literal:

            while not choice:
                choice = input(' / '.join(user_options)+'> ')

                for i, opt in enumerate(user_options):
                    if choice in opt:
                        if not chosen:
                            chosen = opt
                        else:
                            print('Multiple choice selected. Invalid')
                            choice = None
                            break
                if chosen:
                    return chosen
                choice = None
                print('Invalid')
        
        else:
            ''' Standard operation '''

            # preset options
            for i, opt in enumerate(user_options):
                # account for lists / tuples
                if type(opt) in [ type( (0,0) ), type( [1,1] ) ]: 
                    node_name, mission_type_tuple = opt
                    readable_description = "{0} {2} ({1})".format(mission_type_tuple[0], mission_type_tuple[1], node_name)

                    print('({0}) {1}'.format(i, readable_description))
                else: # simple items
                    print('({0}) {1}'.format(i, str(opt) ))
            if random_opt:
                print('({0}) {1}'.format(len(user_options), 'random'))

            # take user selection
            while not choice:
                try:
                    choice = input('(Choice) > ')
                    if choice in ['q','quit']:
                        raise KeyboardInterrupt

                    choice = int(choice)
                    if choice in range(len(user_options) + (1 if random_opt else 0)):
                        if choice == len(user_options):
                            chosen = random.choice(user_options)
                            return chosen

                        return user_options[choice]
                except ValueError as ve:
                    pass
                except KeyboardInterrupt as ki:
                    sys.exit(0) # account for Control-C exit
                choice = None
                print('Invalid')

        return choice

    def load_save_data(self, save_data):
        for nodetype, nodes in save_data['relations'].items():
                for nid, node in nodes.items():
                    # id, ntype, refs, attrs, reltn, checks, abilities
                    print('creating node ',nid, nodetype)
                    self.state.relations[nodetype][nid] = SimulaeNode(  nid,
                                                                        node['nodetype'],
                                                                        node['references'], 
                                                                        node['attributes'],
                                                                        node['relations'],
                                                                        node['checks'],
                                                                        node['abilities'] )