
#from json import JSONEncoder
from .NGIN_utils.ngin_utils import *
from .NGIN_config.madlibs import *

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
POLICY_DISPOSITION = "PolicyDisposition"
REPUTATION = "Reputation"
SOCIAL_DISPOSITION = "SocialDisposition"

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
DEFAULT_PERSONALITY_VALUE = 3 # halfway between 0 and 6

class SimulaeNode:

    # id, ntype, refs, attrs, reltn, checks, abilities

    def __init__(self,  given_id=None, 
                        nodetype=OBJ,
                        references: dict ={
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
            self.References[POLICY] = self.generate_policy()
            
            if self.Nodetype is POI:
                self.References[PERSONALITY] = self.generate_personality()

        self.Attributes = attributes

        self.Relations = {
            CONTENTS:{ nt:{} for nt in NODETYPES},      # organs for POI, items contained for LOC/OBJ
            COMPONENTS:{ nt:{} for nt in NODETYPES},    # limbs for POI, parts for OBJ
            ATTACHMENTS:{ nt:{} for nt in NODETYPES}    # accessories, clothing, equipped items for POI, attachments for OBJ
        }

        if relations is not None:
            for k,v in relations.items():
                self.Relations[k] = v
        
        self.Checks = checks
        self.Abilities = abilities
        
    def keyname(self, *args) -> str:
        return '|'.join(args)
    
    def get_description(self):
        description = ""

        if self.Nodetype == POI:

            associations = self.describe_faction_associations()

            policies = self.describe_political_beliefs()

            personality = self.describe_personality()

            description = "{0}, A {1} year old {2}. Located at {3}\n--- ASSOCIATIONS ---\n{4}\n--- PERSONALITY ---\n{5}\n--- POLITICAL BELIEFS ---\n{6}".format(
                self.get_reference(NAME),
                self.get_attribute("Age"),
                self.get_reference("Gender"),
                self.get_reference(LOC),
                associations,
                personality,
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

    def get_location(self):
        logDebug("get_location()")

        return self.get_reference(LOC)

    def get_adjacent_locations(self):
        logDebug("get_adjacent_locations()")
        
        if ADJACENT in self.References:

            adjacents = self.References[ADJACENT]

            if type(adjacents) == type(""):
                return [adjacents]

            return adjacents
        else:
            return []

    def add_adjacent_location(self, loc, reciprocate=True):
        logDebug("add_adjacent_location(",loc,")")

        self.add_reference(ADJACENT, loc.ID)
        loc.add_reference(ADJACENT, self.ID, reciprocate=False)


    def knows_about(self, node):
        logDebug("knows_about(",node,")", newline=False)

        knows_about = False

        if node.Nodetype in SOCIAL_NODE_TYPES:
            if self.has_relation(node, node.Nodetype): # already has relationship
                knows_about = True

        elif node.Nodetype in INANIMATE_NODE_TYPES:
            
            if self.has_relation(node, node.Nodetype): # already has relationship
                knows_about = True

        logDebug("-> ",knows_about, newline=True)
        return knows_about


    def get_reference(self, key: str) -> str | None:
        logDebug("get_reference(",key,")")
        
        if key in self.References:
            return self.References[key]

        return None

    def set_reference(self, key: str, value: str):
        logDebug("set_reference(",key,value,")")
        self.References[key] = value

    def add_reference(self, key: str, value: str):
        logDebug("add_reference(",key,value,")")
        
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

    def get_attribute(self, key: str) -> int | float | None:
        logDebug("get_attribute(",key,")")

        if not key:
            return None

        attribute = None

        if key in self.Attributes:
            attribute = self.Attributes[key]

        if type(attribute) in [int, float]:
            return attribute
        
        return attribute

    def set_attribute(self, key: str, value: int):
        logDebug("set_attribute(",key,", ",value,")")
        if key in self.Attributes and type(self.Attributes[key]) != type(value):
            logWarning(f"Warning: Overwriting attribute '{key}' of type {type(self.Attributes[key])} with value of type {type(value)}")

        self.Attributes[key] = value

    def determine_relation(self, node, interaction=None):
        logDebug("determining",self,"relationship with",node)

        relationship = {}

        if node.ID not in self.Relations[CONTENTS][node.Nodetype]: # new relationship

            if node.Nodetype in SOCIAL_NODE_TYPES: # other node is a social node

                if self.Nodetype in SOCIAL_NODE_TYPES: # we are also a social node
                    policy_diff = self.policy_diff( node.References[POLICY] )

                    relationship = {
                        NODETYPE : node.Nodetype,
                        STATUS : "new",
                        POLICY : policy_diff,
                        REPUTATION : [0,0],
                        INTERACTIONS : 0,
                        POLICY_DISPOSITION : self.get_policy_disposition(policy_diff[0]),
                    }

                    if node.Nodetype is POI:
                        social_diff = self.social_diff( node.References[PERSONALITY] )
                        relationship[SOCIAL_DISPOSITION] = self.get_social_disposition( social_diff[0] )

                    if interaction != None:
                        
                        if interaction == "Join":
                            relationship[REPUTATION][0] += 10
                            relationship[STATUS] = "Member"
                        
                        else:
                            logWarning("Unhandled interaction type: ",interaction)

                    return relationship

                elif self.Nodetype in INANIMATE_NODE_TYPES: # we are an inanimate node
                    return "Occupant"

            elif node.Nodetype in INANIMATE_NODE_TYPES: # other node is an inanimate node
                return {}
        
            else: 
                logWarning('Unhandled nodetype: ',node.Nodetype)

        elif node.Nodetype in SOCIAL_NODE_TYPES and self.Nodetype in SOCIAL_NODE_TYPES: # we are both social nodes with an existing relationship

            relationship = self.Relations[node.ID]
            
            policy_diff = self.policy_diff( node.references[POLICY] )
            social_disposition = self.social_diff( node.references[PERSONALITY])
            
            relationship[POLICY] = node.Policy
            relationship[POLICY_DISPOSITION] = self.get_policy_disposition(policy_diff[0])
            relationship[SOCIAL_DISPOSITION] = self.get_social_disposition(social_disposition)
            
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
            logWarning("Unhandled relation")


    def update_relation(self, node, interaction=None): # TODO AE: Reimplement 
        logDebug("update_relation(",node,")")
        
        if not node:
            raise ValueError
        
        if node.Nodetype not in self.Relations[CONTENTS]:
            self.Relations[CONTENTS][node.Nodetype] = {}

        self.Relations[CONTENTS][node.Nodetype][node.ID] = self.determine_relation(node, interaction)


    def get_relation(self, node): # TODO AE: Reimplement 
        logDebug("get_relation(",node,")")

        if self.has_relation(node.ID, node.Nodetype):
            return self.Relations[node.Nodetype][node.ID]
        else:
            return self.determine_relation(node)

    def get_relations_by_criteria(self, criteria):
        logDebug("get_relations_by_criteria(",criteria,")")
        
        return [] # TODO AE: implement 
    
    def get_accompanyment(self):
        ''' get_accompanyment() returns a list of ids of actors accompanying this actor '''
        logDebug("get_accompanyment()")
        
        return [nid for nid, relation in self.Relations[POI].items() if relation[STATUS] == "Accompanying"]

    def has_relation( self, key: str, nodetype: str ): # TODO AE: Reimplement 
        logDebug("has_relation(",key,", ",nodetype,")")

        if key in self.Relations.get(nodetype, {}):
            return True
        return False
    
    def set_check(self, key: str, value: bool):
        logDebug("set_check(",key,", ",value,")")

        self.checks[key] = value

    def get_check(self, key:str):
        logDebug("get_check(",key,")")

        if key in self.checks:
            return self.checks[key]
        return None

    def get_default_policy(self):
        logDebug("get_default_policy()")
        
        policy = {}
        
        for k,v in POLICY_SCALE.items():
            policy[k] = [self.get_policy_stance(k, DEFAULT_POLICY_VALUE), DEFAULT_POLICY_VALUE]

        return policy

    def generate_policy(self):
        logDebug("generate_policy()")

        return self.generate_values_for_scales(POLICY_SCALE)
    
    def generate_personality(self):
        logDebug("generate_personality()")

        return self.generate_values_for_scales(PERSONALITY_SCALE)
    
    def generate_values_for_scales(self, scales: dict, std_dev_variance: float = 0.3) -> dict:
        logDebug("generate_values_for_scales(",scales,")")

        values = {}

        # Random values along bell curve adjusted for given scale
        for key in scales.keys():
            selection_index = get_bellcurve_value_for_scale(scales[key], std_dev_variance)
            #trait_value = scales[key][selection_index]
            values[key] = selection_index, random.randrange(1, 10) # belief strength

        return values

    def get_policy_disposition(self, policy_diff_value):
        logDebug("get_policy_disposition(",policy_diff_value,")")

        if policy_diff_value < 0:
            raise ValueError

        # TODO AE: Move descriptions to config
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

    def get_social_disposition(self, social_diff_value):
        logDebug("get_social_disposition(",social_diff_value,")")

        if social_diff_value < 0:
            raise ValueError

        # TODO AE: Move descriptions to config
        elif social_diff_value <= 10:
            return "Friendly"
        elif social_diff_value < 20:
            return "Neutral"
        elif social_diff_value >= 20:
            return "Hostile"

    def policy_diff( self, compare_policy ):
        logDebug("policy_diff(",compare_policy,")")

        summary = {}
        diff = 0

        for factor, policy in self.References[POLICY].items():
            policy, policy_belief_strength = policy

            cmp_factor_policy, cmp_factor_belief_strength = compare_policy[factor]
                        
            policy_index = policy
            cmp_factor_index = cmp_factor_policy

            delta = abs( policy_index - cmp_factor_index )       
            strength_delta = int(abs( policy_belief_strength - cmp_factor_belief_strength ) / 2)

            # TODO AE: Move descriptions to config
            descr = [ "Agreement", "Similar", "Civil", "Disagreement", "Contentious",  "Opposed", "Diametrically-Opposed" ][delta]
            degree = ["", "Leans ", "Slightly ", "Moderately ", "Very ", "Strongly ", "Extremely " ][delta]

            summary[factor] = f"{degree}{descr}"
            
            diff += delta

        return diff, summary
    
    def social_diff( self, compare_personality ):
        logDebug("social_diff(",compare_personality,")")

        summary = {}
        diff = 0

        for key, value in self.References[PERSONALITY].items():
            personality_value_index, personality_value_strength = value

            cmp_personality_value_index, cmp_personality_value_strength = compare_personality[key]
    
            delta = abs( personality_value_index - cmp_personality_value_index )       

            # TODO AE: Move descriptions to config
            descr = [ "Similar", "Somewhat Similar", "Neutral", "Somewhat Different", "Different",  "Very Different", "Opposed" ][delta]
            degree = ["", "Leans ", "Slightly ", "Moderately ", "Very ", "Strongly ", "Extremely " ][delta]

            summary[key] = f"{degree}{descr}"
            
            diff += delta
        
        return diff, summary

    def get_policy_index(self, factor:str, policy:str) -> int:
        logDebug("get_policy_index(",factor,", ",policy,")")

        return POLICY_SCALE[factor].index(policy)

    def get_policy_stance(self, factor: str, index: int) -> str:
        logDebug("get_policy_stance(",factor,", ",index,")")

        return POLICY_SCALE[factor][index]

    def describe_political_beliefs(self):
        logDebug("describe_political_beliefs()")

        summary = ""

        if POLICY not in self.References:
            return ""

        politics = self.References[POLICY]

        for policy, (stance_index, strength) in politics.items():
            if policy not in POLICY_SCALE:
                continue

            if stance_index == 3:  # Indifferent
                continue

            descr = POLICY_BELIEF_STRENGTH_DESCRIPTORS[strength-1]

            stance_descr = POLICY_SCALE[policy][stance_index]

            summary += f"{policy:<18} | {descr} {stance_descr}\n"

        return summary
    
    def describe_personality(self):
        logDebug("describe_personality()")

        if PERSONALITY not in self.References:
            return ""
        
        summary = ""

        personality = self.References[PERSONALITY]

        for trait, (trait_index, strength) in personality.items():
            if trait not in PERSONALITY_SCALE:
                continue

            descr = PERSONALITY_TRAIT_STRENGTH_DESCRIPTORS[strength-1]

            trait_descr = PERSONALITY_SCALE[trait][trait_index]

            summary += f"""{trait:<18} | {descr} {trait_descr}\n"""
        return summary

    def describe_faction_associations(self):
        logDebug("describe_faction_associations()")

        summary = ""

        for sid, relationship in self.Relations[FAC].items():

            summary += f"{sid} {relationship[STATUS]}, "

        return summary

    def toJSON(self):

        try:

            d = self.__dict__

            for nodetype, nodes in self.Relations.items():
                v = {}

                if type(nodes) == type(""):
                    print(f'ERR | Unexpected type in "toJSON(..)" | why is this {nodetype}"nodes" a str?', nodes)
                elif type(nodes) == type([]):
                    print(f'ERR | Unexpected type in "toJSON(..)" | why is this {nodetype}"nodes" a list?', nodes)
                    pass # todo AE: resolve SimulaeNode OBJ.Relations is type list
                else:
                    for node_id, node in nodes.items():
                        if isinstance(node, dict):
                            v[node_id] = {}
                            for k, val in node.items():
                                if hasattr(val, 'toJSON'):
                                    v[node_id][k] = val.toJSON()
                                else:
                                    v[node_id][k] = val
                        elif hasattr(node, 'toJSON'):
                            v[node_id] = node.toJSON()
                        else:
                            v[node_id] = node

                d[RELATIONS][nodetype] = v

            for k,v in self.References.items():
                d[REFERENCES][k] = v

            d[STATUS] = self.Status.toJSON()

            return d

        except Exception as e:
            print("ERROR WHILE SAVING", type(e), str(e))
            return {}


    def from_json(data):
        logDebug("from_json(...)")
        
        try:

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
    logDebug("jsonify(state)")

    d = state.__dict__

    for k,v in state.Relations.items():

        v =  v = { nid:node.__dict__ for nid, node in v.items() }
        d['relations'][k] = v

    return d

def generate_simulae_node(node_type, node_name=None):
    logDebug("generate_simulae_node(",node_type,", ",node_name,")")

    name = node_name

    nodetype = random.choice( NODETYPES ) if node_type == None else node_type
    
    references={
        NAME:name,
    }
    
    attributes = {}
    relations  = { nt:{} for nt in ALL_NODE_TYPES }
    checks     = {}
    abilities  = {}

    if nodetype in INANIMATE_NODE_TYPES:
        
        if nodetype == LOC:
           attributes['max_adjacent_locations'] = random.randrange(1,MAX_ADJACENT_LOCATIONS)

    simulae_node = SimulaeNode( None, nodetype, references, attributes, relations, checks, abilities )

    return simulae_node

def generate_person_simulae_node(node_name=None):
    logDebug("generate_person_simulae_node(",node_name,")")
    ''' generate_person_simulae_node() generates a SimulaeNode of type POI with random attributes '''
    
    person = generate_simulae_node(POI, node_name)

    person.set_attribute("Age", int(random_bell_curve_value(
        min_val=6, 
        max_val=80, 
        average=30, 
        std_dev=15))) # age

    gender = random.choice(["Male","Female"])
    person.set_reference("Gender", gender)
    #person.set_reference("Race", random.choice(["White", "Black", "Asian", "Hispanic", "Middle-Eastern", "Native American", "South Asian"]))

    # generate height & weight
    total_height = random_bell_curve_value(
        min_val = HUMAN_BODY_METRICS[(gender.lower())]["height"]["min"], 
        max_val = HUMAN_BODY_METRICS[(gender.lower())]["height"]["max"],
        average = HUMAN_BODY_METRICS[(gender.lower())]["height"]["avg"],
        std_dev = HUMAN_BODY_METRICS[(gender.lower())]["height"]["stddev"]) # meters

    total_weight = random_bell_curve_value(
        min_val = HUMAN_BODY_METRICS[(gender.lower())]["weight"]["min"], 
        max_val = HUMAN_BODY_METRICS[(gender.lower())]["weight"]["max"],
        average = HUMAN_BODY_METRICS[(gender.lower())]["weight"]["avg"],
        std_dev = HUMAN_BODY_METRICS[(gender.lower())]["weight"]["stddev"]) # meters

    person.set_attribute("Height", round(total_height, 2))
    person.set_attribute("Weight", round(total_weight, 2))

    head, torso, left_arm, right_arm, left_leg, right_leg = generate_person_body(
        gender=gender,
        age=person.get_attribute("Age"),
        height=total_height,
        weight=total_weight,
        complete=True)
    
    person.Relations[COMPONENTS][OBJ][torso.ID] = torso
    person.Relations[COMPONENTS][OBJ][left_arm.ID] = left_arm
    person.Relations[COMPONENTS][OBJ][right_arm.ID] = right_arm
    person.Relations[COMPONENTS][OBJ][left_leg.ID] = left_leg
    person.Relations[COMPONENTS][OBJ][right_leg.ID] = right_leg
    person.Relations[COMPONENTS][OBJ][head.ID] = head

    return person

def generate_person_body(gender: str, age: int, height: float, weight: float, complete: bool = True):
    logDebug("generate_person_body()")

    leg_height = height * HUMAN_BODY_METRICS["limbs"]["leg_height"]
    torso_height = height * HUMAN_BODY_METRICS["limbs"]["torso_height"]
    head_height = height * HUMAN_BODY_METRICS["limbs"]["head_height"]
    #feet_height = total_height * HUMAN_BODY_METRICS["limbs"]["foot_height"]
    arm_height = height * HUMAN_BODY_METRICS["limbs"]["arm_height"]

    head_weight = weight * HUMAN_BODY_METRICS["limbs"]["head_height"]        # 7%
    leg_weight = weight * HUMAN_BODY_METRICS["limbs"]["leg_height"]        # 35%
    torso_weight = weight * HUMAN_BODY_METRICS["limbs"]["torso_height"]        # 40%
    arm_weight = weight * HUMAN_BODY_METRICS["limbs"]["arm_height"]        # 15%
    hand_weight = weight * HUMAN_BODY_METRICS["limbs"]["hand_weight"]       # 1%
    foot_weight = weight * HUMAN_BODY_METRICS["limbs"]["foot_height"]        # 2%  

    # add standard things like limbs and organs

    torso = SimulaeNode( nodetype=OBJ, references={ NAME:"Torso" }, attributes={"height": torso_height, "weight": torso_weight} )
    skull = SimulaeNode( nodetype=OBJ, references={ NAME:"Skull" } )
    left_arm = SimulaeNode( nodetype=OBJ, references={ NAME:"Left Arm" }, attributes={"height": arm_height, "weight": arm_weight} )
    right_arm = SimulaeNode( nodetype=OBJ, references={ NAME:"Right Arm" }, attributes={"height": arm_height, "weight": arm_weight} )
    left_leg = SimulaeNode( nodetype=OBJ, references={ NAME:"Left Leg" }, attributes={"height": leg_height, "weight": leg_weight} )
    right_leg = SimulaeNode( nodetype=OBJ, references={ NAME:"Right Leg" }, attributes={"height": leg_height, "weight": leg_weight} )
    left_hand = SimulaeNode( nodetype=OBJ, references={ NAME:"Left Hand" }, attributes={"weight": hand_weight} )
    right_hand = SimulaeNode( nodetype=OBJ, references={ NAME:"Right Hand" }, attributes={"weight": hand_weight} )
    head = SimulaeNode( nodetype=OBJ, references={ NAME:"Head" }, attributes={"height": head_height, "weight": head_weight} )

    # add organs
    heart = SimulaeNode( nodetype=OBJ, references={ NAME:"Heart" } )
    lungs = SimulaeNode( nodetype=OBJ, references={ NAME:"Lungs" } )
    brain = SimulaeNode( nodetype=OBJ, references={ NAME:"Brain" } )
    liver = SimulaeNode( nodetype=OBJ, references={ NAME:"Liver" } )
    kidneys = SimulaeNode( nodetype=OBJ, references={ NAME:"Kidneys" } )
    stomach = SimulaeNode( nodetype=OBJ, references={ NAME:"Stomach" } )
    intestines = SimulaeNode( nodetype=OBJ, references={ NAME:"Intestines" } )
    eyes = SimulaeNode( nodetype=OBJ, references={ NAME:"Eyes" } )
    ears = SimulaeNode( nodetype=OBJ, references={ NAME:"Ears" } )
    nose = SimulaeNode( nodetype=OBJ, references={ NAME:"Nose" } )
    mouth = SimulaeNode( nodetype=OBJ, references={ NAME:"Mouth" } )
    hair = SimulaeNode( nodetype=OBJ, references={ NAME:"Hair" } )
    teeth = SimulaeNode( nodetype=OBJ, references={ NAME:"Teeth" } )

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

    return head, torso, left_arm, right_arm, left_leg, right_leg


def get_bellcurve_value_for_scale(scale_list: list, std_dev: float, std_deviation_frac: float = 0.3) -> int:
    logDebug("get_bellcurve_value_for_scale(",scale_list,")")
    ''' get_bellcurve_value_for_scale(scale_list) returns an index into the given scale_list
        using a bell curve distribution centered on the middle of the scale_list
    '''

    if (not scale_list) or (len(scale_list) == 0):
        raise ValueError("Scale list is empty")
    elif len(scale_list) == 1:
        return 0
    elif len(scale_list) % 2 == 0:
        raise ValueError("Scale list must have an odd number of elements to have a central average")

    min_index = 0
    max_index = len(scale_list) - 1
    average_index = (min_index + max_index) / 2

    index = int(random_bell_curve_value(min_index, max_index, average_index, std_dev, std_deviation_frac))

    return index


def random_bell_curve_value(min_val: float, max_val: float, average: float, std_dev: float, std_deviation_frac: float = None) -> float:
    logDebug("random_bell_curve_value(",min_val,", ",max_val,", ",average,", ",std_deviation_frac,")")
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

    if std_dev is None and std_deviation_frac is not None:
        std_dev = (max_val - min_val) * std_deviation_frac

    # Generate values until one falls within range (clipping is optional but can bias the curve)
    while True:
        value = random.gauss(average, std_dev)
        if min_val <= value <= max_val:
            return round(value, 2)