from NGIN_console import *

class NGIN(NGIN_console):

    def __init__(self, mission_struct, madlibs, save_file=None):
        super().__init__(mission_struct, madlibs, save_file)

        if not save_file:
            for node in self.generate_state(4): # generate start state with 4 initial nodes
                self.add_node(node)

    def add_node(self, node):
        self.state.relations[node.nodetype][node.id] = node

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
            

    def choose_mission(self, actor_node=None, num_opts=3 ):
        ''' To add more interractivity and user-control
                this function will give several available options to allow
                the player to 'control' their actions and interract
                with other nodes in a manner of their choice.
        '''
        options = []

        while len(options) < num_opts:

            ## Generate randomized node and action ##

            ntype = random.choice([ nt for nt in ["POI","PTY","OBJ","LOC"] if len(self.state.relations[nt]) >= 1 ])            
            subj = random.choice( list(self.state.relations[ ntype ].values()) )

            if subj.nodetype in ["POI","PTY"]:

                ## Determine friend/enemy disposition if given actor-node 
                if actor_node is not None:
                    actor_node.update_relationship( subj, reciprocate=True )
                    disposition = actor_node.relations[subj.nodetype][subj.id]["Disposition"]
                else:
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
        pass

    def remove_node(self, node):
        pass

    def destroy_node(self, node):
        node.status = Status.DEAD
        #del self.state.relations[subject.nodetype][subject.id]

    def validate_state(self):
        has_entities = False
        for nt in NODETYPES:
            if len(self.state.relations[nt]) >= 1:
                has_entities = True

        if not has_entities:
            self.add_node(SimulaeNode.generate_simulae_node())

    def display_state(self):
        print('\nGamestate:')

        for node in [ node for nodetype, nodes in self.state.relations.items() for nid, node in nodes.items() ]:
            if node.status is not Status.DEAD:
                pprint( node.summary() )

    def handle_mission(self, mission, subject):
        print(  '\n(',mission[1],') [',
                mission[0],subject.summary(),']')

        # Handle success

        success = self.user_choice( ['yes','no'], literal=True )

        if success == 'yes':

            if mission[0] in ['Eliminate','Destroy']:
                # find and remove subject
                self.destroy_node(subject)
                
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

def try_json_load(filename):

    try:
        return json.load(open(filename))
    except Exception as e:
        print("Failed to load from JSON : ", filename)
        print("Error msg:",e)
        return {}


def main():
    
    ''' required import(s) '''

    mission_struct = try_json_load( sys.argv[1] )
    print("Loaded mission_struct")
    save_file = try_json_load( sys.argv[2] )
    print("Loaded save_file [",sys.argv[2],"]")

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


    print('### ### ###\nCOMPLETE THE REFACTOR OF SimulaeNode.policies !!!!!\n### ### ###')
    #sys.exit(1);

    ngin.start()



if __name__ == '__main__':
    main()






