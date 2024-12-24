from NGIN_console import *
from ngin_utils import *
from FactionGenerator.faction_generator import *

from SimulaeNode import *

class NGIN():

    def __init__(self, mission_struct, settings, madlibs, save_file=None, is_console=True):
        
        if not mission_struct or mission_struct == None:
            raise ValueError("Missing required data: mission_struct")

        if not settings or settings == None:
            raise ValueError("Missing required data: settings")

        if not madlibs or madlibs == None:
            raise ValueError("Missing required data: madlibs")
        
        self.mission_struct = mission_struct
        self.madlibs = madlibs
        self.settings = settings
        self.state = SimulaeNode(
                        "state",        # id
                        "",             # nodetype
                        {},             # references
                        {},
                        {               # relations
                            FAC:{},
                            PTY:{},
                            POI:{},
                            OBJ:{},
                            LOC:{}
                        },
                        {},
                        {}
                    )

        self.world_root = None
        self.taken_names = []
        self.is_console = is_console

        if not save_file:
            self.generate_new_world() 
            
        self.get_location_map()


    def start(self):

        if self.is_console:
            self.start_console()


    def start_console(self):
        ''' Iterates through the game state generating missions based on
                available nodes in the state.
        '''

        actor = self.get_simulae_node_by_id(self.select_actor(), POI)

        input('<Press "ENTER" to START>')

        while True:

            os.system('clear') # clear screen

            self.validate_state()

            self.display_state()

            subject, mission = self.choose_mission(actor_node=actor, num_opts=5)

            self.resolve_mission(mission, subject)

            cmd = input('continue [enter] / [q]uit ?> ')
            if cmd in ['q','quit']:
                sys.exit(0) 


    def select_actor(self):

        print("Select actor node: (Choose your character)")

        options = { node.summary():nid for nid, node in self.state.relations[POI].items()}

        selected_node = user_choice( user_options=list(options.keys()), random_opt=True )

        print("selected -> ",selected_node,f'[{options[selected_node]}]')
        # return the actor node id
        return options[selected_node]


    def generate_new_world(self):

        print('generating new world')

        # generate networked map of locations

        # small, medium, or large?
       
        self.world_root = generate_simulae_node(LOC, self.get_new_name())
        self.add_node(self.world_root)

        world_size = self.settings['world_size']
        lo, hi = self.settings['world_sizes'][world_size]

        num_world_locs = random.randrange(lo, hi)

        for i in range(num_world_locs):
            loc = self.generate_location()

            self.attach_loc(loc)
            

    def get_location_map(self):
        
        locations = self.state.relations[LOC]

        loc_map = {}

        for loc_id, loc in locations.items():
            
            debug(f"{loc.nodetype} {loc_id}")
            loc_map[loc_id] = loc.get_adjacent_locations()

            for adj_id in loc_map[loc_id]:
                debug(f"\tLOC {locations[adj_id]}")

        return loc_map

    def get_simulae_node_by_id(self, nid: str, nodetype: str=None):

        if not nid:
            raise ValueError("'nid' cannot be null/empty")

        if not nodetype:

            for nt in ALL_NODE_TYPES:
                if nt in self.state.relations and nid in self.state.relations[nt]:
                    return self.state.relations[nt][nid]

        else:
            return self.state.relations[nodetype][nid]


    def attach_loc(self, new_loc):
        
        # get 'stickiness' setting -> chance to attach to 'current' node
        stickiness = WORLD_GEN_STICKINESS

        # add to world
        self.add_node(new_loc)

        nodes = [self.world_root.id]
        
        while nodes:
            node_id = nodes.pop()
            node = self.get_simulae_node_by_id(node_id, LOC)

            adjs = node.get_adjacent_locations()

            if not adjs or len(adjs) < node.get_attribute('max_adjacent_locations'):
                
                if random.random() < stickiness:
                    node.add_reference('adjacent',new_loc.id) # attach to current location
                    return
                
                if not adjs and not nodes:
                    node.add_reference('adjacent', new_loc.id)  # force-attach to last available node
                    return
            

            nodes = nodes + adjs
                


    def generate_location(self):

        # single-feature-location or multi-location (2-6)

        location = generate_simulae_node(LOC, self.get_new_name())

        # generate feature(s)?


        # generate population
        population = self.generate_population(location)

        for entity in population:

            self.add_node(entity)

            location.update_relation(entity)

        return location


    def generate_population(self, location):

        # individual or group?

        population = []
        
        if random.random() < WORLD_GEN_POPULATION_GROUP_CHANCE:
            population = self.generate_group(location)
            
        else:
            population = [self.generate_individual(location)]

        return population


    def generate_group(self, location):

        # generate new faction
        faction = self.generate_faction()
        self.add_node(faction)

        # small medium or large? -> generate more individuals
        group_size = random.choice( list(self.settings['groups'].keys()) )

        lo, hi = int(self.settings['groups'][group_size][0]), int(self.settings['groups'][group_size][1])
        num_individuals = random.randrange(lo, hi)

        debug(f"Generating group of size {num_individuals}")

        group = []
        for i in range(num_individuals):
            individual = self.generate_individual(location)
            individual.update_relation(faction)

            group.append(individual)

        return group


    def generate_individual(self, location):

        individual = generate_simulae_node(POI, self.get_new_name())

        individual.nodetype = POI
        individual.update_relation(location)
        
        return individual

    def add_node(self, node):
        debug(f"add_node({node.summary()})")

        self.state.relations[node.nodetype][node.id] = node

        if 'name' in node.references:
            self.taken_names = node.references['name']

        if node.nodetype == LOC:
            if 'LOC_num' not in self.state.attributes:
                self.state.attributes['LOC_num'] = 0

            self.state.attributes['LOC_num'] += 1


    def generate_faction(self):
        debug("generate_faction()")
        

        # choose organization subtype
        orgtype = random.choice(self.madlibs['Entities'])
        
        # madlibs name generation
        name = random.choice(self.madlibs['Nouns']) + ('-'+random.choice(self.madlibs['Nouns']) if random.random() >= 0.6 else '' )
        suffix = random.choice(self.madlibs['Suffixes'][orgtype]) if random.random() >= 0.1 else ''
        name += ' '+suffix
        # acronym for quick/short reference (display purposes)
        acronym = ''.join( [ l for l in name if l.isupper() ] )

        # randomize policy
        policy = self.generate_policy(orgtype)

        # fix this
        faction = generate_simulae_node(FAC, name)
        faction.references[POLICY] = policy

        return faction


    def generate_policy(self, orgtype=None):

        policies = self.madlibs['Policies']

        if orgtype:
            policies = self.madlibs['Preset-Policies'][orgtype]

        policy = {}

        for k,v in policies.items():
            #               position            weight
            policy[k] = [ random.choice(v), random.random() ]

        return policy


    def get_new_name(self):

        name = random.choice(self.madlibs['Nouns'])

        while name in self.taken_names and name != "":
            name = random.choice( self.madlibs['Nouns'] )

        return name 


    def generate_element( self, nodetype ):
        ''' creates a new node with random attributes ''' 

        name = self.get_new_name()
        nodetype = random.choice( NODETYPES ) if not nodetype else nodetype
        references = {}
        attributes = {}
        relations  = {}
        checks     = {}
        abilities  = {}

        # id, nodetype, refs, attrs, reltn, checks, abilities
        return SimulaeNode( name, nodetype, references, attributes, relations, checks, abilities )
            

    def choose_mission(self, actor_node=None, num_opts=3 ):
        debug(f"choose_mission( actor: {actor_node.summary()}, num_opts={num_opts})")

        ''' To add more interractivity and user-control
                this function will give several available options to allow
                the player to 'control' their actions and interract
                with other nodes in a manner of their choice.
        '''
        options = []

        while len(options) < num_opts:

            ## Generate randomized node and action ##

            ntype = random.choice([ nt for nt in NODETYPES if len(self.state.relations[nt]) >= 1 ])            
            subj = random.choice( list(self.state.relations[ ntype ].values()) )

            if subj.nodetype in PEOPLE_NODE_TYPES:

                ## Determine friend/enemy disposition if given actor-node 
                if actor_node is not None:
                    actor_node.update_relation( subj )
                    disposition = actor_node.relations[subj.nodetype][subj.id]["Disposition"]
                    debug(f"actor:{actor_node.id} <-{disposition}-> subject:{subj}")
                else:
                    disposition = "Neutral"

            else:
                disposition = "Neutral"

            opt = ( subj, random.choice( self.mission_struct[disposition][subj.nodetype] ) )
            options.append(opt)


        choice = user_choice( options, random_opt=True )

        return subj, choice[1]


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

    def display_state(self, actor_node=None):
        print('\nGamestate:')

        for nodetype, nodes in self.state.relations.items():
            print(f"### {nodetype} ###")

            for node_id, node in nodes.items():
                if node.status is not Status.DEAD:

                    if actor_node: # from perspective of...
                        if not actor_node.knows_about(node):
                            continue

                    print(node.summary())

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

                if subject.nodetype in INANIMATE_NODE_TYPES:

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

    if not sys.argv or len(sys.argv) <= 3:
        print("Must specify application data files to start\n"
            +"[mission_struct] [ngin_settings] [save_file:optional]")

        sys.argv = ['script.py','story_struct.json','ngin_settings.json','madlibs.json']

    mission_struct = load_json_from_file( sys.argv[1] )

    ngin_settings = load_json_from_file( sys.argv[2])

    madlibs = load_json_from_file(sys.argv[3])

    save_file = None
    if len(sys.argv) >= 5:
        save_file = load_json_from_file( sys.argv[4] )

    # Setup 
    ngin = NGIN( mission_struct, ngin_settings, madlibs, save_file )

    # Start
    ngin.start()



if __name__ == '__main__':
    main()






