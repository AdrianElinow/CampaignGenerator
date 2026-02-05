
#from json import JSONEncoder
from NGIN_utils.ngin_utils import *
from NGIN_config.madlibs import *

FAC = 'FAC'
POI = 'POI'
PTY = 'PTY'
LOC = 'LOC'
OBJ = 'OBJ'

NAME = "Name"
POLICY = "Policy"
PERSONALITY = "Personality"
ADJACENT = "Adjacent"
STATUS = "Status"
INTERACTIONS = "Interactions"
REPUTATION = "Reputation"
DISPOSITION = "Disposition"

ID = "ID"
REFERENCES = "References"
NODETYPE = "Nodetype"
ATTRIBUTES = "Attributes"
CONTENTS = "Contents"
COMPONENTS = "Components"
ATTACHMENTS = "Attachments"
RELATIONS = "Relations"
RELATIVE_TYPES = [CONTENTS, COMPONENTS, ATTACHMENTS]
CHECKS = "Checks"
ABILITIES = "Abilities"

ALL_NODE_TYPES = [FAC,POI,PTY,LOC,OBJ]
NODETYPES = [POI,PTY,LOC,OBJ] # person, people, place, thing
SOCIAL_NODE_TYPES = [FAC,POI,PTY]
GROUP_NODE_TYPES = [FAC,PTY]
PEOPLE_NODE_TYPES = [POI,PTY]
INANIMATE_NODE_TYPES = [LOC,OBJ]

DEFAULT_POLICY_VALUE = 4 # halfway between 1 and 7

class SimulaeNode:

    # id, ntype, refs, attrs, reltn, checks, abilities

    def __init__(self,  given_id=None, 
                        nodetype=OBJ,
                        references={
                            NAME:None,
                        }, 
                        attributes={}, 
                        relations=None, 
                        checks={}, 
                        abilities={}):

        self.ID = given_id if given_id else str(uuid.uuid1())
        self.Status = Status.ALIVE
        self.References = references
        self.Nodetype = nodetype

        if self.Nodetype in SOCIAL_NODE_TYPES:
            self.References[POLICY] = {policy: (DEFAULT_POLICY_VALUE, DEFAULT_POLICY_VALUE) for policy in POLICY_SCALE}

        self.Attributes = attributes

        self.Relations = {
            CONTENTS:{ nt:{} for nt in NODETYPES},      # organs
            COMPONENTS:{ nt:{} for nt in NODETYPES},    # limbs
            ATTACHMENTS:{ nt:{} for nt in NODETYPES}    # accessories, clothing, equipped items
        }

        if relations is not None:
            for k,v in relations.items():
                self.Relations[k] = v
        
        self.Checks = checks
        self.Abilities = abilities

    def get_description(self):
        description = ""

        if self.Nodetype == POI:

            associations = self.describe_faction_associations()

            policies = self.describe_political_beliefs()

            description = "{0}, A {1} year old {2} {3}. Located at {4}. {5}. {6}".format(self.get_reference(NAME),
                self.get_attribute("Age"),
                self.get_reference("Race"),
                self.get_reference("Gender"),
                self.get_reference(LOC),
                associations,
                policies)

        return description

    def summary(self):
        summary = "{{{0}:{1}}} {2}".format(self.Nodetype, 
            self.get_reference(NAME),
            self.get_description(),
            f"located at {self.get_reference(LOC)}" if LOC in self.References else "")

        return summary

    def __str__(self):
        return self.get_reference(NAME)


    def check_membership(self, node): # TODO AE: Reimplement 
        ''' check_membership(..., node) checks for relations between self and given node
                if node is of types OBJ or LOC, checks of self has ownership of node
                if node is of types FAC or PTY, checks that node has membership with self
        '''

        if not (node and node.Nodetype and node.ID):
            raise ValueError

        if self.Nodetype in PEOPLE_NODE_TYPES:

            # check self's ownership of node
            if node.Nodetype in INANIMATE_NODE_TYPES and node.ID in self.Relations['PPT'][node.Nodetype]:
                return True
            # check self's membership as apart of node
            elif node.Nodetype in GROUP_NODE_TYPES and node.Relations[self.Nodetype][self.ID][STATUS] == 'Member':
                return True

        elif self.Nodetype == FAC:

            if node.Nodetype in INANIMATE_NODE_TYPES and node.ID in self.Relations['PPT'][node.Nodetype]:
                return True
            elif node.Nodetype in PEOPLE_NODE_TYPES and self.Relations[node.Nodetype][node.ID][STATUS] == "Member":
                return True

        return False

    def get_location(self):

        return self.get_reference(LOC)

    def get_adjacent_locations(self):
        
        if ADJACENT in self.References:

            adjacents = self.References[ADJACENT]

            if type(adjacents) == type(""):
                return [adjacents]

            return adjacents
        else:
            return []

    def add_adjacent_location(self, loc, reciprocate=True):
        
        self.add_reference(ADJACENT, loc.ID)
        loc.add_reference(ADJACENT, self.ID, reciprocate=False)


    def knows_about(self, node):
        debug("knows_about(",node,")")

        knows_about = False

        if node.Nodetype in SOCIAL_NODE_TYPES:
            if self.has_relation(node, node.Nodetype): # already has relationship
                knows_about = True

        elif node.Nodetype in INANIMATE_NODE_TYPES:
            
            if self.has_relation(node, node.Nodetype): # already has relationship
                knows_about = True

        debug("-> ",knows_about)
        return knows_about


    def get_reference(self, key: str):
        debug("get_reference(",key,")")
        
        if key in self.References:
            return self.References[key]

        return None

    def set_reference(self, key: str, value: str):
        debug("set_reference(",key,value,")")
        self.References[key] = value

    def add_reference(self, key: str, value: str):
        debug("add_reference(",key,value,")")
        
        if key in self.References:
            
            reference = self.References[key]

            if type(reference) == type(""):
                if reference is not value:
                    self.References[key] = [reference, value]
                    
            elif type(reference) == type([]):
                if value not in reference:
                    self.References[key].append(value)

        else:
            self.References[key] = value

    def get_attribute(self, key: str):
        debug("get_attribute(",key,")")

        if key in self.Attributes:
            return self.Attributes[key]

        return None

    def set_attribute(self, key: str, value: int):
        self.Attributes[key] = value

    def determine_relation(self, node, interaction=None):
        debug("determining",self,"relationship with",node)

        relationship = {}

        if node.ID not in self.Relations[node.Nodetype]: # new relationship

            if node.Nodetype in SOCIAL_NODE_TYPES: # other node is a social node

                if self.Nodetype in SOCIAL_NODE_TYPES: # we are also a social node
                    policy_diff = self.policy_diff( node.References[POLICY] )

                    relationship = {
                        "Nodetype":node.Nodetype,
                        STATUS:"new",
                        POLICY:policy_diff,
                        REPUTATION:[0,0],
                        INTERACTIONS:0,
                        DISPOSITION:self.get_policy_disposition(policy_diff[0])
                    }

                    if interaction != None:
                        
                        if interaction == "Join":
                            relationship[REPUTATION][0] += 10
                            relationship[STATUS] = "Member"

                    return relationship

                elif self.Nodetype in INANIMATE_NODE_TYPES: # we are an inanimate node
                    return "Occupant"

            elif node.Nodetype in INANIMATE_NODE_TYPES: # other node is an inanimate node
                return {}
        
            else: 
                debug('Unhandled nodetype: ',node.Nodetype)

        elif node.Nodetype in SOCIAL_NODE_TYPES and self.Nodetype in SOCIAL_NODE_TYPES: # we are both social nodes with an existing relationship

            relationship = self.Relations[node.ID]
            
            policy_diff = self.policy_diff( node.references[POLICY] )
            
            relationship[POLICY] = node.Policy
            relationship[DISPOSITION] = self.get_policy_disposition(policy_diff[0])
            
            if interaction != None:
                        
                if interaction == "join":
                    relationship[REPUTATION][interaction[0]] += interaction[1]
                    relationship[STATUS] = "Member"
                if interaction == "accompany":
                    relationship[REPUTATION][interaction[0]] += interaction[1]
                    relationship[STATUS] = "Accompanying"

            relationship[INTERACTIONS] += 1

            # update w changes
            return relationship
            
        else:
            debug("Unhandled relation")


    def update_relation(self, node, interaction=None): # TODO AE: Reimplement 
        
        if not node:
            raise ValueError
        
        if node.Nodetype in self.Relations:
            self.Relations[node.Nodetype] = {}

        self.Relations[node.Nodetype][node.ID] = self.determine_relation(node, interaction)


    def get_relation(self, node): # TODO AE: Reimplement 

        if self.has_relation(node.ID, node.Nodetype):
            return self.Relations[node.Nodetype][node.ID]
        else:
            return self.determine_relation(node)

    def get_relations_by_criteria(self, criteria):
        
        return [] # TODO AE: implement 
    
    def get_accompanyment(self):
        ''' get_accompanyment() returns a list of ids of actors accompanying this actor '''
        
        return [nid for nid, relation in self.Relations[POI].items() if relation[STATUS] == "Accompanying"]

    def has_relation( self, key: str, nodetype: str ): # TODO AE: Reimplement 
        
        if key in self.Relations[nodetype]:
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

        for factor, policy in self.References[POLICY].items():
            policy, policy_belief_strength = policy

            cmp_factor_policy, cmp_factor_belief_strength = compare_policy[factor]
                        
            policy_index = policy
            cmp_factor_index = cmp_factor_policy

            delta = abs( policy_index - cmp_factor_index )       
            strength_delta = int(abs( policy_belief_strength - cmp_factor_belief_strength ) / 2)

            descr = [ "Agreement", "Similar", "Civil", "Disagreement", "Contentious",  "Opposed", "Diametrically-Opposed" ][delta]
            degree = ["", "Leans ", "Slightly ", "Moderately ", "Very ", "Strongly ", "Extremely " ][delta]

            summary[factor] = f"{degree}{descr}"
            
            diff += delta

        return diff, summary

    def get_policy_index(self, factor:str, policy:str) -> int:

        return POLICY_SCALE[factor].index(policy)

    def get_policy_stance(self, factor: str, index: int) -> str:

        return POLICY_SCALE[factor][index]

    def describe_political_beliefs(self):
        summary = """
> Political Beliefs:
"""

        if POLICY not in self.References:
            return ""

        politics = self.References[POLICY]

        for policy, (stance, strength) in politics.items():
            if policy not in POLICY_SCALE:
                continue

            if stance == 3:  # Indifferent
                continue

            descr = POLICY_BELIEF_STRENGTH_DESCRIPTORS[strength-1]

            stance_descr = POLICY_SCALE[policy][stance]

            summary += f"""{descr} {stance_descr}.
"""

        return summary

    def describe_faction_associations(self):
        summary = "Associations: "

        for sid, relationship in self.Relations[FAC].items():

            summary += f"{sid} {relationship[STATUS]}, "

        return summary

    def toJSON(self):
        try:

            d = self.__dict__

            for nodetype, nodes in self.Relations.items():
                v = {}

                if type(nodes) == type(""):
                    print(f'why is this {nodetype}"nodes" a str?', nodes)
                elif type(nodes) == type([]):
                    pass # todo AE: resolve SimulaeNode OBJ.Relations is type list
                else:
                    for node_id, node in nodes.items():
                        if type(node) == type({}):

                            for k, v in node.items():
                                v[node_id][k] = v.toJSON()

                            #v[node_id] = node
                        else:
                            v[node_id] = node.toJSON()

                d[RELATIONS][nodetype] = v

            for k,v in self.References.items():
                d[REFERENCES][k] = v

            d[STATUS] = self.Status.toJSON()

            return d

        except Exception as e:
            print("ERROR WHILE SAVING", type(e), e.message)
            return {}


    def from_json(data):
        try:

            print('from_json')

            if type(data) != type({}):
                raise ValueError(f"from_json | invalid data type: {type(data)}")

            keys = list(data.keys())

            n_id = data[ID] if 'id' in keys else None
            n_type = data[NODETYPE] if 'nodetype' in keys else None
            n_refs = data[REFERENCES] if 'references' in keys else {}
            n_attr = data[ATTRIBUTES] if 'attributes' in keys else {}
            n_rels = data[RELATIONS] if 'relations' in keys else {}
            n_checks = data[CHECKS] if 'checks' in keys else {}
            n_abilities = data[ABILITIES] if 'abilities' in keys else {}

            if not n_id or not n_type:
                raise ValueError(f"Cannot determine ID or nodetype of entity |\n {data}")

            relations = { nt:{} for nt in ALL_NODE_TYPES }
            for ntype, nodes in n_rels.items():
                print(ntype)
                for nid, ndata in nodes.items():
                    node = SimulaeNode.from_json(ndata)
                    print('->',node.ID)
                    relations[ntype][node.ID] = node

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

    for k,v in state.Relations.items():

        v =  v = { nid:node.__dict__ for nid, node in v.items() }
        d['relations'][k] = v

    return d

def generate_simulae_node(node_type, node_name=None):

    name = node_name

    nodetype = random.choice( NODETYPES ) if node_type == None else node_type
    
    _policies = list(POLICY_SCALE.keys())

    references={
        NAME:name,
        POLICY: { policy : [POLICY_SCALE[policy][DEFAULT_POLICY_VALUE], DEFAULT_POLICY_VALUE] for policy in POLICY_SCALE.keys() },
    }
    
    attributes = {}
    relations  = { nt:{} for nt in ALL_NODE_TYPES }
    checks     = {}
    abilities  = {}

    if nodetype in SOCIAL_NODE_TYPES:
        # Random Policy values
        for policy in _policies:
            references[POLICY][policy] = random.choice(POLICY_SCALE[policy]), random.randrange(1,10)

    if nodetype in INANIMATE_NODE_TYPES:
        
        if nodetype == LOC:
           attributes['max_adjacent_locations'] = random.randrange(1,MAX_ADJACENT_LOCATIONS)

    simulae_node = SimulaeNode( name, nodetype, references, attributes, relations, checks, abilities )

    return simulae_node

def generate_person_simulae_node(node_name=None):
    ''' generate_person_simulae_node() generates a SimulaeNode of type POI with random attributes '''
    
    person = generate_simulae_node(POI, node_name)

    person.set_attribute("Age", random.randrange(16, 65)) # age
    person.set_reference("Gender", random.choice(["Male","Female"]))
    person.set_reference("Race", random.choice(["White", "Black", "Asian", "Hispanic", "Middle-Eastern", "Native American", "South Asian"]))

    # generate height & weight
    total_height = random_bell_curve_value(0.9, 2.5, 1.75, 0.15) # meters
    total_weight = random_bell_curve_value(50, 120, 75, 0.15) # kg

    leg_height = total_height * .45
    torso_height = total_height * .35
    head_height = total_height * .15
    feet_height = total_height * .05

    head_weight = total_weight * .08        # 7%
    leg_weight = total_weight * .175        # 35%
    torso_weight = total_weight * .5        # 40%
    arm_weight = total_weight * .075        # 15%
    hand_weight = total_weight * .005       # 1%
    foot_weight = total_weight * .01        # 2%  

    # add standard things like limbs and organs

    torso = SimulaeNode( nodetype=OBJ, references={ "owner":person.ID, NAME:"Torso" }, attributes={"height": torso_height, "weight": torso_weight} )
    skull = SimulaeNode( nodetype=OBJ, references={ "owner":person.ID, NAME:"Skull" } )
    left_arm = SimulaeNode( nodetype=OBJ, references={ "owner":person.ID, NAME:"Left Arm" }, attributes={"height": arm_weight, "weight": arm_weight} )
    right_arm = SimulaeNode( nodetype=OBJ, references={ "owner":person.ID, NAME:"Right Arm" }, attributes={"height": arm_weight, "weight": arm_weight} )
    left_leg = SimulaeNode( nodetype=OBJ, references={ "owner":person.ID, NAME:"Left Leg" }, attributes={"height": leg_height, "weight": leg_weight} )
    right_leg = SimulaeNode( nodetype=OBJ, references={ "owner":person.ID, NAME:"Right Leg" }, attributes={"height": leg_height, "weight": leg_weight} )
    left_hand = SimulaeNode( nodetype=OBJ, references={ "owner":person.ID, NAME:"Left Hand" }, attributes={"height": hand_weight, "weight": hand_weight} )
    right_hand = SimulaeNode( nodetype=OBJ, references={ "owner":person.ID, NAME:"Right Hand" }, attributes={"height": hand_weight, "weight": hand_weight} )
    head = SimulaeNode( nodetype=OBJ, references={ "owner":person.ID, NAME:"Head" }, attributes={"height": head_height, "weight": head_weight} )

    # add organs
    heart = SimulaeNode( nodetype=OBJ, references={ "owner":person.ID, NAME:"Heart" } )
    lungs = SimulaeNode( nodetype=OBJ, references={ "owner":person.ID, NAME:"Lungs" } )
    brain = SimulaeNode( nodetype=OBJ, references={ "owner":person.ID, NAME:"Brain" } )
    liver = SimulaeNode( nodetype=OBJ, references={ "owner":person.ID, NAME:"Liver" } )
    kidneys = SimulaeNode( nodetype=OBJ, references={ "owner":person.ID, NAME:"Kidneys" } )
    stomach = SimulaeNode( nodetype=OBJ, references={ "owner":person.ID, NAME:"Stomach" } )
    intestines = SimulaeNode( nodetype=OBJ, references={ "owner":person.ID, NAME:"Intestines" } )
    eyes = SimulaeNode( nodetype=OBJ, references={ "owner":person.ID, NAME:"Eyes" } )
    ears = SimulaeNode( nodetype=OBJ, references={ "owner":person.ID, NAME:"Ears" } )
    nose = SimulaeNode( nodetype=OBJ, references={ "owner":person.ID, NAME:"Nose" } )
    mouth = SimulaeNode( nodetype=OBJ, references={ "owner":person.ID, NAME:"Mouth" } )
    #skin = SimulaeNode( name="Skin", nodetype=OBJ )
    hair = SimulaeNode( nodetype=OBJ, references={ "owner":person.ID, NAME:"Hair" } )
    teeth = SimulaeNode( nodetype=OBJ, references={ "owner":person.ID, NAME:"Teeth" } )
    #lh_nails = SimulaeNode( name="Nails", nodetype=OBJ )
    #rh_nails = SimulaeNode( name="Nails", nodetype=OBJ )

    torso.Relations[CONTENTS][OBJ][heart.ID] = heart
    torso.Relations[CONTENTS][OBJ][lungs.ID] = lungs
    
    torso.Relations[CONTENTS][OBJ][liver.ID] = liver
    torso.Relations[CONTENTS][OBJ][kidneys.ID] = kidneys
    torso.Relations[CONTENTS][OBJ][stomach.ID] = stomach
    torso.Relations[CONTENTS][OBJ][intestines.ID] = intestines
    ### etc...

    head.Relations[COMPONENTS][OBJ][skull.ID] = skull
    head.Relations[CONTENTS][OBJ][brain.ID] = brain
    head.Relations[CONTENTS][OBJ][eyes.ID] = eyes
    head.Relations[CONTENTS][OBJ][ears.ID] = ears
    head.Relations[CONTENTS][OBJ][nose.ID] = nose
    head.Relations[CONTENTS][OBJ][mouth.ID] = mouth
    head.Relations[CONTENTS][OBJ][hair.ID] = hair
    head.Relations[CONTENTS][OBJ][teeth.ID] = teeth

    left_arm.Relations[COMPONENTS][OBJ][left_hand.ID] = left_hand
    right_arm.Relations[COMPONENTS][OBJ][right_hand.ID] = right_hand 
    
    #left_hand.Relations[CONTENTS][OBJ][lh_nails.ID] = lh_nails
    #right_hand.Relations[CONTENTS][OBJ][rh_nails.ID] = rh_nails

    #person.Relations[COMPONENTS][OBJ][skin.ID] = skin

    person.Relations[COMPONENTS][OBJ][torso.ID] = torso
    person.Relations[COMPONENTS][OBJ][left_arm.ID] = left_arm
    person.Relations[COMPONENTS][OBJ][right_arm.ID] = right_arm
    person.Relations[COMPONENTS][OBJ][left_leg.ID] = left_leg
    person.Relations[COMPONENTS][OBJ][right_leg.ID] = right_leg
    person.Relations[COMPONENTS][OBJ][head.ID] = head

    return person


def random_bell_curve_value(min_val: float, max_val: float, average: float, std_deviation_frac: float = 0.15) -> float:
    """
    Generate a realistic random value along a bell curve (normal distribution),
    constrained within min and max, centered on average.

    Parameters:
    - min_val (float): The minimum allowed value.
    - max_val (float): The maximum allowed value.
    - average (float): The central mean value.
    - std_deviation_frac (float): Fraction of (max - min) to use as standard deviation.
                             Default is 15% for moderate variance.

    Returns:
    - float: Random value distributed normally, clipped to [min_val, max_val].
    """

    std_dev = (max_val - min_val) * std_deviation_frac

    # Generate values until one falls within range (clipping is optional but can bias the curve)
    while True:
        value = random.gauss(average, std_dev)
        if min_val <= value <= max_val:
            return round(value, 2)