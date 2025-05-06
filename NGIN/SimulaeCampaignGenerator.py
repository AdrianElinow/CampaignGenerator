import sys
import os
from NGIN_console import *
from NGIN_utils.ngin_utils import *
from NGIN_config.ngin_missions import *
from FactionGenerator.faction_generator import *
from SimulaeNode import *

class NGIN():

    def __init__(self, mission_struct, settings, save_file=None, is_console=True):
        
        if not mission_struct or mission_struct == None:
            raise ValueError("Missing required data: mission_struct")

        if not settings or settings == None:
            raise ValueError("Missing required data: settings")

        self.mission_struct = mission_struct
        self.settings = settings
        self.state = SimulaeNode(
                        "state",        # id
                        "state",             # nodetype
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

        try:
            if save_file:
                self.import_world(save_file)
        except Exception as e:
            print(f'Unable to import world data from save file | {e}')

        if not self.state.relations or not self.state.references:
            print('No world data... generating...')
            self.generate_new_world()


        self.print_location_map()


    def start(self):

        if self.is_console:
            self.start_console()


    def import_world(self, save_file):
        print('importing world data...')

        self.state = SimulaeNode.from_json(save_file)


    def save_to_file(self, filename: str):

        data = self.state.toJSON()

        save_json_to_file(filename, data, pretty=True)


    def start_console(self):
        ''' Iterates through the game state generating missions based on
                available nodes in the state.
        '''

        actor = self.get_simulae_node_by_id(self.select_actor(randomized=True), POI)

        while True:

            os.system('clear') # clear screen

            self.validate_state()

            #self.display_state()

            options = self.get_actions(actor=actor)

            mission = self.select_mission(options)

            self.resolve_mission(actor, mission)

            cmd = input('continue [enter] / [q]uit ?> ')
            if cmd in ['q','quit']:
                sys.exit(0) 


    def select_actor(self, randomized=False):

        options = { node.summary():nid for nid, node in self.state.relations[POI].items()}

        if not options:
            raise Exception("No POI nodes to select from...")

        if not randomized:
            print("Select actor node: (Choose your character)")
            selected_node = user_choice( user_options=list(options.keys()), random_opt=True )
        else:
            selected_node = random.choice(list(options.keys()))

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
            

    def print_location_map(self):
        
        locations = self.state.relations[LOC]

        loc_map = {}

        for loc_id, loc in locations.items():
            
            print(f"{loc.nodetype} {loc_id}")
            loc_map[loc_id] = loc.get_adjacent_locations()

            for adj_id in loc_map[loc_id]:
                print(f"\tLOC {locations[adj_id]}")

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

    def get_simulae_nodes_by_reference(self, reference_key: str, reference_value: str =None ,nodetype: str=None):
        debug(f"get_simulae_nodes_by_reference( reference_key: {reference_key}, reference_value: {reference_value}, nodetype: {nodetype} )")

        if nodetype:
            # return all nodes with reference to reference_key (and if provided a reference_value, must also have that value associated with the key)
            
            selected = {}

            for snid, sn in self.state.relations[nodetype].items():

                if reference_value:
                    if reference_value == sn.get_reference(reference_key):
                        selected[snid] = sn

                #if sn.get_reference(reference_key):
                    #selected[snid] = sn

            return selected


        else:
            nodes_with_reference = {}

            for nodetype, nodes in self.state.relations.items():
                nodes_with_reference = nodes_with_reference | self.get_simulae_nodes_by_reference(reference_key, reference_value, nodetype)

            return nodes_with_reference

    def attach_loc(self, new_loc):
        
        # get 'stickiness' setting -> chance to attach to 'current' node
        stickiness = WORLD_GEN_STICKINESS

        # add to world
        self.add_node(new_loc)

        visited = [] 
        nodes = [self.world_root.id]
        
        while nodes:
            node_id = nodes.pop()
            visited.append(node_id)
            node = self.get_simulae_node_by_id(node_id, LOC)
            
            # filter visited nodes to prevent infinite loop due to circular references
            adjs = [ adj for adj in node.get_adjacent_locations() if adj not in visited ]

            if not adjs or len(adjs) < node.get_attribute('max_adjacent_locations'):
                
                if random.random() < stickiness:
                    node.add_reference('adjacent',new_loc.id) # attach to current location
                    new_loc.add_reference('adjacent',node.id)
                    return
                
                if not adjs and not nodes:
                    node.add_reference('adjacent', new_loc.id)  # force-attach to last available node
                    new_loc.add_reference('adjacent',node.id)
                    return
            

            nodes = nodes + adjs
                


    def generate_location(self):

        # single-feature-location or multi-location (2-6)

        location = generate_simulae_node(LOC, self.get_new_name())

        # generate feature(s)?


        # generate population
        population, faction = self.generate_population(location)

        for entity in population:

            self.add_node(entity)

            # set entity's location
            entity.add_reference(LOC, location.id)

            if faction: # set faction ownership of location
                location.references[FAC] = faction.id

        return location


    def generate_population(self, location):

        # individual or group?

        population = []
        faction = None

        if random.random() < WORLD_GEN_POPULATION_GROUP_CHANCE:
            population, faction = self.generate_group(location)
            
        else:
            population = [self.generate_individual(location)]

        return population, faction


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

            individual.references[FAC] = faction.id

            #individual.add_reference(FAC, faction.id)
            #individual.update_relation(faction)

            group.append(individual)

        return group, faction


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
        orgtype = random.choice(FACTION_TYPES)
        
        # madlibs name generation
        name = random.choice(MADLIBS_NOUNS) + ('-'+random.choice(MADLIBS_NOUNS) if random.random() >= 0.6 else '' )
        suffix = random.choice(MADLIBS_SUFFIXES[orgtype]) if random.random() >= 0.1 else ''
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

        policies = POLICY_SCALE

        if orgtype:
            policies = PRESET_POLICIES[orgtype]

        policy = {}

        for k,v in policies.items():
            #               position            weight
            policy[k] = [ random.choice(v), random.random() ]

        return policy


    def get_new_name(self):

        name = random.choice( MADLIBS_NOUNS )

        while name in self.taken_names and name != "":
            name = random.choice( MADLIBS_NOUNS )

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
            

    def nodes_are_adjacent(self, node1, node2):

        loc1 = node1.get_reference(LOC)
        loc2 = node2.get_reference(LOC)

        if loc1 == loc2:
            return True

        return False


    def get_actions(self, actor):

        # handle inanimates
        if actor.nodetype not in SOCIAL_NODE_TYPES:
            return []

        options = []

        # evaluate immediate options:

        # current location / adjacent entities
        actor_loc = actor.get_reference(LOC)

        loc = self.get_simulae_node_by_id(actor_loc, LOC)
        print('Current Location:',loc.id)
        options.append(self.get_actions_for_node(actor, loc, note="current location"))


        # same location?
        adjacents = self.get_simulae_nodes_by_reference(LOC, reference_value=actor_loc)

        if not adjacents:
            print("No adjacent entities found")

        for adj_id, adj in adjacents.items():
            options.append(self.get_actions_for_node(actor, adj, note="adjacent entity"))

        
        # evaluate movement/travel options
        adjacent_locations = loc.get_adjacent_locations()

        if not adjacent_locations:
            print("No adjacent locations found")

        for adj_id in adjacent_locations:
            adj_loc = self.get_simulae_node_by_id(adj_id, LOC)
            options.append(self.get_actions_for_node(actor, adj_loc, note="Travel to", is_adjacent=True))

        return options


    def get_actions_for_node(self, actor, target, note=None, is_adjacent=False):
        
        if type(target) == type(""):
            print(target)

        # handle inanimates
        if actor.nodetype not in SOCIAL_NODE_TYPES:
            return []

        disposition = "Neutral"

        if target.nodetype in SOCIAL_NODE_TYPES:
            relationship = actor.determine_relation(target)
            disposition = relationship["Disposition"]

        if not is_adjacent:
            actions = NGIN_MISSIONS[disposition][target.nodetype]
        else:
            actions = [['Travel','Overt']]

        return target, actions, note


    def select_mission(self, missions):
        
        mission_index = []
        count = 0

        selection_idx = 0
        selected_mission = None
        selected_target = None

        while not selected_mission:

            while not selected_target:
                for idx, mission in enumerate(missions):
                    target, options, note = mission
                    print(f"{idx:3} | [{note:^16}] |{target.summary()} ")

                selection_idx = robust_int_entry("Select Target > ", 0, len(missions))
                selected_target = missions[selection_idx]

            t, options, note = selected_target

            if len(options) > 1:

                for idx, opt in enumerate(options):
                    print(f"{idx:3} | ({opt[1]:^9}) {opt[0]}")

                selection_idx = robust_int_entry("Select Action (or '-1' to revert to target selection) > ",-1,len(options))

                if selection_idx == -1:
                    selected_target = None
                    continue
            else:
                selection_idx = 0

            selected_mission = options[selection_idx]
            selected_target = t

        return selected_target, selected_mission


    def generate_mission(self, actor, mission):

        target, m = mission
        action, liminality = m

        debug(f"{actor.summary()} -> ({liminality}) {action} {target.summary()}")




    def resolve_mission(self, actor, mission):
        
        target, m = mission
        action, liminality = m

        debug(f"{actor.summary()} -> ({liminality}) {action} {target.summary()}")

        if target.nodetype in SOCIAL_NODE_TYPES:
            print('social')

            relationship = actor.get_relation(target)
            pprint(relationship)
            
            disposition = relationship['Disposition']

            print('disposition:',disposition)

            pprint(NGIN_MISSIONS[disposition][target.nodetype])


        elif target.nodetype in INANIMATE_NODE_TYPES:
            print('inanimate')

            if target.has_relation(actor.id, FAC):

                relationship = actor.get_relation( target.get_relation(FAC) )

            if action == 'Travel':

                if self.can_perform_action(target, action):
                    print(f'{actor} traveling to {target}')

                    actor.set_reference(LOC, target.id)         # set actor loc to target
                    target.add_reference('occupant', actor.id) # add actor as occupant to target

    def can_perform_action(self, target, action):
        return True


    def remove_node(self, node):
        pass


    def destroy_node(self, node):
        node.status = Status.DEAD


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
                        if not self.nodes_are_adjacent(actor_node, node) and not actor_node.knows_about(node):
                            continue

                    print(node)


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
    
    # Import NGIN
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


    mission_struct = load_json_from_file( "NGIN/NGIN_config/story_struct.json" )
    ngin_settings = load_json_from_file( "NGIN/NGIN_config/ngin_settings.json" )

    save_file = None
    if len(sys.argv) >= 5:
        save_file = load_json_from_file( sys.argv[1] )

    # Setup 
    ngin = NGIN( mission_struct, ngin_settings, save_file )

    # Start

    try:

        ngin.start()

    except Exception as e:
        print(e)
    finally:
        print('saving...')
        ngin.save_to_file("save_file.json")


if __name__ == '__main__':
    main()






