from NGIN_console import *
from ngin_utils import *

class NGIN(NGIN_console):

    def __init__(self, mission_struct, settings, madlibs, save_file=None):
        super().__init__(mission_struct, settings, madlibs, save_file)

        self.world_root = None

        if not save_file:
            self.generate_new_world() 
            
        self.get_location_map()

    def generate_new_world(self):

        print('generating new world')

        # generate networked map of locations

        # small, medium, or large?
       
        self.world_root = generate_simulae_node('root_loc',LOC)
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
            
            print(loc)
            loc_map[loc_id] = loc.get_adjacent_locations()

            for adj_id in loc_map[loc_id]:
                print(f"\t{locations[adj_id]}")

        return loc_map

    def get_simulae_node_by_id(self, id: str, nodetype: str):

        if not id:
            raise ValueError("'id' cannot be null/empty")

        if not nodetype:
            raise ValueError("'nodetype' cannot be null/empty")
        
        return self.state.relations[nodetype][id]


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

        loc_id = f"loc_{self.state.attributes['LOC_num']}"

        return generate_simulae_node(loc_id, LOC)


    def generate_population(self, location):

        # individual or group?

        population = []
        
        if random.random() < WORLD_GEN_POPULATION_GROUP_CHANCE:
            
            population = self.generate_group(location.id)
            
        else:
            population = [self.generate_individual(location.id)]

        return population

        pass

    def generate_group(self):

        faction = self.generate_faction()


        # small medium or large? -> generate more individuals

        group_size = random.choice( self.settings['groups'] )
        
        num_individuals = random.randrange(group_size[0], group_size[1])
    
        



        # generate new faction

        pass

    def generate_individual(self, location_id):
        
        individual = self.generate_element()

        individual.nodetype = POI
        
        return individual

    def add_node(self, node):
        self.state.relations[node.nodetype][node.id] = node

        if 'LOC_num' not in self.state.attributes:
            self.state.attributes['LOC_num'] = 0

        self.state.attributes['LOC_num'] += 1


    def generate_faction(self):
        
        faction = self.generate_element()



    def generate_element( self ):
        ''' creates a new node with random attributes ''' 

        name = random.choice( [ m for m in self.madlibs \
            if m not in [ subj.name for subj in ( self.state ) ]] )

        nodetype = random.choice( NODETYPES )
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

            ntype = random.choice([ nt for nt in NODETYPES if len(self.state.relations[nt]) >= 1 ])            
            subj = random.choice( list(self.state.relations[ ntype ].values()) )

            if subj.nodetype in PEOPLE_NODE_TYPES:

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

    if not sys.argv or len(sys.argv) < 3:
        print("Must specify application data files to start\n"
            +"[mission_struct] [ngin_settings] [save_file:optional]")
        sys.argv = ['script.py','story_struct.json','ngin_settings.json','madlibs.json']

    mission_struct = load_json_from_file( sys.argv[1] )

    ngin_settings = load_json_from_file( sys.argv[2])

    madlibs = load_json_from_file(sys.argv[3])

    save_file = None
    if len(sys.argv) >= 5:
        save_file = load_json_from_file( sys.argv[4] )

    ngin = NGIN( mission_struct, ngin_settings, madlibs, save_file )


    print('### ### ###\nCOMPLETE THE REFACTOR OF SimulaeNode.policies !!!!!\n### ### ###')
    #sys.exit(1);

    ngin.start()



if __name__ == '__main__':
    main()






