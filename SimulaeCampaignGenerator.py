
import json, sys, random, os
from pprint import pprint

from SimulaeNode import SimulaeNode


class NGIN:

    def __init__(self, mission_struct, madlibs, save_file=None ):
        self.mission_struct = mission_struct
        self.madlibs = madlibs
        self.state = state = SimulaeNode(
                        "state",
                        "",
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

            print('found save file')

            for nodetype, nodes in save_file['relations'].items():
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
        else:
            self.state = self.generate_state(4) # generate start state with 4 initial nodes


    def generate_element( self ):
        ''' creates a new node with random attributes ''' 

        name = random.choice( [ m for m in self.madlibs \
            if m not in [ subj.name for subj in ( self.state ) ]] )

        nodetype = random.choice( ['POI','PTY','OBJ','LOC'] )
        references = {}
        attributes = {}
        relations  = {}
        checks     = {}
        abilities  = {}

        # id, nodetype, refs, attrs, reltn, checks, abilities
        return SimulaeNode( name, nodetype, references, attributes, relations, checks, abilities )


    def generate_state( self, num_nodes ):
        ''' generates multiple new random nodes to (re)populate the game-state '''

        n_state = []
        for i in range(num_nodes):
            n_state.append(self.generate_element())
        return n_state
            

    def choose_mission(self, actor_node=None, num_opts=3 ):
        ''' To add more interractivity and user-control
                this function will give several available options to allow
                the player to 'control' their actions and interract
                with other nodes in a manner of their choice.
        '''
        options = []

        while len(options) < 3:

            ntype = random.choice([ nt for nt in ["POI","PTY","OBJ","LOC"] if len(self.state.relations[nt]) >= 1 ])
            #print(list(self.state.relations[ ntype ].values()))

            subj = random.choice( list(self.state.relations[ ntype ].values()) )

            #print('subj: ',subj)

            if subj.nodetype in ["POI","PTY"]:
                #actor_node.update_relationship( subj, reciprocate=True )
                #disposition = actor_node.relations[subj.nodetype][subj.id]["Disposition"]
                disposition = "Neutral"
            else:
                disposition = "Neutral"

            opt = ( subj, random.choice( self.mission_struct[disposition][subj.nodetype] ) )
            options.append(opt)


        choice = self.user_choice( options, random_opt=True )

        return subj, choice[1], self.state


    def generate_event( self ):
        ''' Selects a node as event basis, then generates an event based on 
                the node's type. Events are similar to missions, but are
                essentially the mission outcomes of other entities
        '''

        # choose node as event basis
        subj = random.choice(self.state)
        name, disp, objective, interractions = subj.unpack()

        # avoid modifying hostile nodes to maintain tension
        if disp in ['Neutral','Friendly']:
            roll = int(random.random() * 100)

            if roll < 25:
                print(name,'has', \
                    ('been captured by opfor' if objective in ['LOC','OBJ'] \
                    else "defected to the opfor"))

                subject_index = self.state.index(subj)

                # find and modify subject in game-state
                subj.disposition = "Hostile"
                subj.interractions += 1

                if subject_index:
                    self.state[subject_index] = subj

            elif roll < 50:
                print(name, 'has been', \
                    ('Destroyed' if objective in ['LOC','OBJ'] \
                    else 'Killed'))

                # find and remove subject in game-state
                self.state.remove(subj)

            # no mission for these types of random events
            return subj, None, self.state

        # 
        return  subj, \
                random.choice(self.mission_struct[disp][objective]), \
                self.state
        pass


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
                    print(chosen)
                    return chosen
                choice = None
                print('Invalid')
        
        else:
            ''' Standard operation '''

            # preset options
            for i, opt in enumerate(user_options):
                # account for lists / tuples
                if type(opt) in [ type( (0,0) ), type( [1,1] ) ]: 
                    print('({0}) {1}'.format(i, ' '.join([ e.summary() if type(e) == type(SimulaeNode()) else str(e) for e in opt ])))
                else: # simple items
                    print('({0}) {1}'.format(i, opt.summary() if type(opt) == type(SimulaeNode()) else str(opt) ))
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
                            print(chosen)
                            return chosen
                        print(user_options[choice])
                        return user_options[choice]
                except ValueError as ve:
                    pass
                except KeyboardInterrupt as ki:
                    sys.exit(0) # account for Control-C exit
                choice = None
                print('Invalid')

        return choice



    def remove_node(self, node):
        ''' not yet implemented '''
        pass


    def save(self):
        ''' not yet implemented '''
        pass

    def start(self):

        ''' Iterates through the game state generating missions based on
                available nodes in the state.
        '''

        input('starting>')

        while True:

            os.system('clear') # clear screen


            print('\nNodes:')

            for node in [ node for nodetype, nodes in self.state.relations.items() for nid, node in nodes.items() ]:
                pprint( (node.id, node.nodetype) )


            # generate mission

            subject, mission, self.state = self.choose_mission(  )
            print(  '\n(',mission[1],') [',
                    mission[0],subject.summary(),']')


            # Handle success

            success = self.user_choice( ['yes','no'], literal=True )

            if success == 'yes':

                if mission[0] in ['Eliminate','Destroy']:
                    # find and remove subject
                    del self.state.relations[subject.nodetype][subject.id]

                elif mission[0] in ['Capture']:

                    if subject.nodetype in ['LOC','OBJ']:

                        self.state.relations[subject.nodetype][subject.id].relations

                        #self.state.remove(subject)
                        # find and modify subject
                        #subject.disposition = "Friendly"

                        #self.state.append(subject)

                    else:
                        # find and remove subject
                        del self.state.relations[subject.nodetype][subject.id]

            '''
            if random.random() <= 0.5:
                # generate new element to keep sim going
                print('\nNew Intel')
                intel = self.generate_element()
                pprint(('discovered '+intel.__str__()))
                self.state.append(intel)

            if random.random() <= 0.4:
                # generate random event to keep things interesting
                subject, mission, self.state = self.generate_event()

                if mission:
                    print(  '\n(',mission[1],') [',
                            mission[0],subject.name,'] {',
                            subject.disposition,subject.nodetype,'}')

                    if mission[0] in ['Eliminate','Destroy']:
                        # find and remove subject in game-state
                        self.state.remove(subject)
            '''

            cmd = input('continue [enter] / [q]uit ?> ')
            if cmd in ['q','quit']:
                sys.exit(0)

def main():
    
    ''' required import(s) '''
    mission_struct = json.load( open( sys.argv[1] ) )
    save_file = json.load( open(sys.argv[2]) )

    print(save_file)

    madlibs = [
        "Alpha",
        "Beta",
        "Delta",
        "Zeta",
        "Omicron",
        "Omega",
        "Lambda",
        "Tau",
        "Gamma",
        "Sigma",
        "Eagle",
        "Wolf",
        "Spider",
        "Siege",
        "Sanguine",
        "Bear",
        "Hound",
        "Phoenix",
        "Dragon",
        "Lion",
        "Gorilla",
        "Rhino",
        "Storm",
        "Shadow",
        "Nocturn",
        "Prime",
        "Zeus",
        "Essence",
        "Banshee",
        "Specter",
        "Typhoon",
        "Pinnacle",
        "Odin",
        "Silver",
        "Platinum",
        "Titan",
        "Heart",
        "Karma",
        "Angel",
        "Demon",
        "Arcane",
        "Mystic",
        "Jupiter",
        "Mars",
        "Meridian",
        "Atlas",
        "Raptor",
        "Void",
        "Hurricane",
        "Harbor",
        "Cold",
        "Jet",
        "Global",
        "Green",
        "Red",
        "Blue",
        "Tap",
        "Soul",
        "Slick",
        "Omen",
        "Arm",
        "Revelation",
        "November",
        "Reach",
        "Winter",
        "Twilight",
        "Quad",
        "Tri",
        "Saturn",
        "Ward",
        "Violet",
        "Steel",
        "Granite",
        "Stone",
        "Slate",
        "First",
        "Federal",
        "Statement",
        "Macguffin",
        "United",
        "King",
        "Queen",
        "Sultan",
        "Atom",
        "Cellular",
        "Spruce",
        "Black",
        "Executive",
        "Admin",
        "Diesel"
    ]

    ngin = NGIN( mission_struct, madlibs, save_file )

    ngin.start()

    ngin.save()



if __name__ == '__main__':
    main()






