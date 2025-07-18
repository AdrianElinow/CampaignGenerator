
#from json import JSONEncoder
from NGIN.NGIN_utils.ngin_utils import *
from NGIN.NGIN_config.madlibs import *

FAC = 'FAC'
POI = 'POI'
PTY = 'PTY'
LOC = 'LOC'
OBJ = 'OBJ'

NAME = "name"
POLICY = "policy"
ADJACENT = "adjacent"

CONTENTS = "Contents"
COMPONENTS = "Components"
ATTACHMENTS = "Attachments"
RELATIONS = [CONTENTS, COMPONENTS, ATTACHMENTS]

ALL_NODE_TYPES = [FAC,POI,PTY,LOC,OBJ]
NODETYPES = [POI,PTY,LOC,OBJ] # person, people, place, thing
SOCIAL_NODE_TYPES = [FAC,POI,PTY]
GROUP_NODE_TYPES = [FAC,PTY]
PEOPLE_NODE_TYPES = [POI,PTY]
INANIMATE_NODE_TYPES = [LOC,OBJ]

DEFAULT_POLICY_VALUE = 3 # halfway between 1 and 5

class SimulaeNode:

    # id, ntype, refs, attrs, reltn, checks, abilities

    def __init__(self,  given_id=None, 
                        nodetype=OBJ,
                        references={
                            NAME:None,
                            FAC:None,
                        }, 
                        attributes={}, 
                        relations=None, 
                        checks={}, 
                        abilities={}):

        self.id = given_id if given_id else uuid.uuid1()
        self.status = Status.ALIVE
        self.references = references
        self.nodetype = nodetype

        if self.nodetype in SOCIAL_NODE_TYPES:
            self.references[POLICY] = self.get_default_policy()

        self.attributes = attributes

        if relations == None:
            relations = { CONTENTS:{ nt:{} for nt in NODETYPES}, COMPONENTS:{ nt:{} for nt in NODETYPES}, ATTACHMENTS:{ nt:{} for nt in NODETYPES} }

        self.relations = relations

        self.checks = checks
        self.abilities = abilities

    def summary(self):
        return "{{{0}:{1}}} {2} {3}".format(self.nodetype, self.references[NAME], f"affiliated with {self.references[FAC]}" if FAC in self.references and self.references[FAC] else "", f"located at {self.references[LOC]}" if LOC in self.references else "")

    def __str__(self):
        return self.summary()


    def check_membership(self, node): # TODO AE: Reimplement 
        ''' check_membership(..., node) checks for relations between self and given node
                if node is of types OBJ or LOC, checks of self has ownership of node
                if node is of types FAC or PTY, checks that node has membership with self
        '''

        if not (node and node.nodetype and node.id):
            raise ValueError

        if self.nodetype in PEOPLE_NODE_TYPES:

            # check self's ownership of node
            if node.nodetype in INANIMATE_NODE_TYPES and node.id in self.relations['PPT'][node.nodetype]:
                return True
            # check self's membership as apart of node
            elif node.nodetype in GROUP_NODE_TYPES and node.relations[self.nodetype][self.id]['Disposition'] == 'Member':
                return True

        elif self.nodetype == FAC:

            if node.nodetype in INANIMATE_NODE_TYPES and node.id in self.relations['PPT'][node.nodetype]:
                return True
            elif node.nodetype in PEOPLE_NODE_TYPES and self.relations[node.nodetype][node.id]['Disposition'] == "Member":
                return True

        return False

    def get_location(self):

        return self.get_reference(LOC)

    def get_adjacent_locations(self):
        
        if ADJACENT in self.references:

            adjacents = self.references[ADJACENT]

            if type(adjacents) == type(""):
                return [adjacents]

            return adjacents
        else:
            return []

    def add_adjacent_location(self, loc, reciprocate=True):
        
        self.add_reference(ADJACENT, loc.id)
        loc.add_reference(ADJACENT, self.id, reciprocate=False)


    def knows_about(self, node): # TODO AE: Reimplement 

        if node.nodetype in SOCIAL_NODE_TYPES:
            if self.has_relation(node, node.nodetype): # already has relationship
                return True

        if node.nodetype in INANIMATE_NODE_TYPES:
            
            if self.has_relation(node, node.nodetype): # already has relationship
                return True

        return False


    def get_reference(self, key: str):
        
        if key in self.references:
            return self.references[key]

        return None

    def set_reference(self, key: str, value: str):
        self.references[key] = value

    def add_reference(self, key: str, value: str):
        
        if key in self.references:
            
            reference = self.references[key]

            if type(reference) == type(""):
                if reference is not value:
                    self.references[key] = [reference, value]
                    
            elif type(reference) == type([]):
                if value not in reference:
                    self.references[key].append(value)

        else:
            self.references[key] = value

    def get_attribute(self, key: str):
        debug("get_attribute(",key,")")

        if key in self.attributes:
            return self.attributes[key]

        return None

    def set_attribute(self, key: str, value: int):
        self.attributes[key] = value

    def determine_relation(self, node): # TODO AE: Reimplement 

        if node.id not in self.relations[node.nodetype]:

            if node.nodetype in SOCIAL_NODE_TYPES:

                # social relationship
                if self.nodetype in SOCIAL_NODE_TYPES:
                    policy_diff = self.policy_diff( node.references['policy'] )

                    return {
                        "nodetype":node.nodetype,
                        "status":"new",
                        POLICY:policy_diff,
                        "Reputation":[0,0],
                        "Interractions":1,
                        "Disposition":self.get_policy_disposition(policy_diff[0])
                    }

                elif self.nodetype in INANIMATE_NODE_TYPES:
                    return "occupant"

            elif node.nodetype in INANIMATE_NODE_TYPES:
                return {}
        
            else:
                debug('Unhandled nodetype: ',node.nodetype)

        elif node.nodetype in SOCIAL_NODE_TYPES and self.nodetype in SOCIAL_NODE_TYPES:

            relationship = self.relations[node.id]
            
            policy_diff = self.policy_diff( node.references[POLICY] )
            
            relationship[POLICY] = node.policy
            relationship["Disposition"] = self.get_policy_disposition(policy_diff[0])
            
            interaction = None

            if interaction != None:
                relationship['Reputation'][interaction[0]] += interaction[1]

            relationship["Interactions"] += 1

            # update w changes
            return relationship
            
        else:
            debug("Unhandled relation")


    def update_relation(self, node, interaction=None): # TODO AE: Reimplement 
        
        if not node:
            raise ValueError
        
        if node.nodetype in self.relations:
            self.relations[node.nodetype] = {}

        self.relations[node.id] = self.determine_relation(node)


    def get_relation(self, node): # TODO AE: Reimplement 

        if self.has_relation(node.id, node.nodetype):
            return self.relations[node.nodetype][node.id]
        else:
            return self.determine_relation(node)

    def get_relations_by_criteria(self, criteria):
        
        return [] # TODO AE: implement 

    def has_relation( self, key: str, nodetype: str ): # TODO AE: Reimplement 
        
        if key in self.relations[nodetype]:
            return True
        return False
    
    def set_check(self, key: str, value: bool):
        self.checks[key] = value

    def get_check(self, key:str):
        if key in self.checks:
            return self.checks[key]
        return None

    def get_default_policy(self):
        
        policy = {}
        
        for k,v in POLICY_SCALE.items():
            policy[k] = [self.get_policy_stance(k, DEFAULT_POLICY_VALUE), DEFAULT_POLICY_VALUE]

        return policy

    def generate_policy(self):

        policy = {}

        for k,v in POLICY_SCALE.items():
            #               position            weight
            policy[k] = [ random.choice(v), random.random() ]

        return policy

    def get_policy_disposition(self, policy_diff_value):

        if policy_diff_value < 0:
            raise ValueError

        elif policy_diff_value <= 10:
            return "Friendly"
        elif policy_diff_value < 20:
            return "Neutral"
        elif policy_diff_value >= 20:
            return "Hostile"
        '''    
        elif policy_diff_value == 0:
            return "Perfectly Aligned"
        elif policy_diff_value < 5:
            return "Aligned"
        elif policy_diff_value < 10:
            return "Neutral"
        elif policy_diff_value < 15:
            return "Opposed"
        elif policy_diff_value < 20:
            return "Strongly Opposed"
        elif policy_diff_value > 20:
            return "Diametrically Opposed"
        '''

    def policy_diff( self, compare_policy ):

        summary = {}
        diff = 0

        for factor, policy in self.references[POLICY].items():
            
            cmp_factor = compare_policy[factor]
            if type(cmp_factor) == type([]):    # for factor values [ policy, degree ]
                cmp_factor = cmp_factor[0]

            delta = abs( self.get_policy_index(factor, policy) - self.get_policy_index( factor, cmp_factor ) )

            summary[factor] = [ "Agreement", "Civil", "Contentious",  "Opposition", "Diametrically Opposed" ][delta]
            diff += delta

        return diff, summary

    def get_policy_index(self, factor:str, policy:str) -> int:

        return POLICY_SCALE[factor].index(policy)

    def get_policy_stance(self, factor: str, index: int) -> str:

        return POLICY_SCALE[factor][index]

    def toJSON(self):
        try:

            d = self.__dict__

            for nodetype, nodes in self.relations.items():
                v = {}

                if type(nodes) == type(""):
                    print(f'why is this {nodetype}"nodes" a str?', nodes)
                elif type(nodes) == type([]):
                    pass # todo AE: resolve SimulaeNode OBJ.relations is type list
                else:
                    for node_id, node in nodes.items():
                        v[node_id] = node.toJSON()

                d['relations'][nodetype] = v

            for k,v in self.references.items():
                d['references'][k] = v

            d['status'] = self.status.toJSON()

            return d

        except Exception as e:
            print(e)
            return {}


    def from_json(data):
        try:

            print('from_json')

            if type(data) != type({}):
                raise ValueError(f"from_json | invalid data type: {type(data)}")

            keys = list(data.keys())

            n_id = data['id'] if 'id' in keys else None
            n_type = data['nodetype'] if 'nodetype' in keys else None
            n_refs = data['references'] if 'references' in keys else {}
            n_attr = data['attributes'] if 'attributes' in keys else {}
            n_rels = data['relations'] if 'relations' in keys else {}
            n_checks = data['checks'] if 'checks' in keys else {}
            n_abilities = data['abilities'] if 'abilities' in keys else {}

            if not n_id or not n_type:
                raise ValueError(f"Cannot determine ID or nodetype of entity |\n {data}")

            relations = { nt:{} for nt in ALL_NODE_TYPES }
            for ntype, nodes in n_rels.items():
                print(ntype)
                for nid, ndata in nodes.items():
                    node = SimulaeNode.from_json(ndata)
                    print('->',node.id)
                    relations[ntype][node.id] = node

            n = SimulaeNode(n_id, 
                n_type, n_refs, n_attr, relations, n_checks, n_abilities)
        
            return n   

        except Exception as e:
            print(e)     

        return None


def _json_get_value(obj):

    if type(obj) == type(""):
        return obj
    elif type(obj) == SimulaeNode:
        return obj.toJSON()

class Status(Enum):
    ''' Simulae Node status '''
    ALIVE = 0
    DEAD = 1

    def toJSON(self):
        if self == 0:
            return "ALIVE"
        elif self == 1:
            return "DEAD"

def jsonify( state ):

    d = state.__dict__

    for k,v in state.relations.items():

        v =  v = { nid:node.__dict__ for nid, node in v.items() }
        d['relations'][k] = v

    return d

def generate_random_simulae_node(node_type, node_name=None, faction=None):

    name = node_name

    nodetype = random.choice( NODETYPES ) if node_type == None else node_type
    
    _policies = list(POLICY_SCALE.keys())

    references={
        NAME:name,
        FAC:None,
        POLICY:{}
    }
    
    attributes = {}
    relations  = { nt:{} for nt in ALL_NODE_TYPES }
    checks     = {}
    abilities  = {}

    # Set Faction association
    if faction:
        references[FAC] = faction.id

    if nodetype in SOCIAL_NODE_TYPES:
        # Random Policy values
        for policy in _policies:
            references[POLICY][policy] = random.choice(POLICY_SCALE[policy])

    if nodetype in INANIMATE_NODE_TYPES:
        
        if nodetype == LOC:
           attributes['max_adjacent_locations'] = random.randrange(1,MAX_ADJACENT_LOCATIONS)

    # id, nodetype, refs, attrs, reltn, checks, abilities
    return SimulaeNode( name, nodetype, references, attributes, relations, checks, abilities )


