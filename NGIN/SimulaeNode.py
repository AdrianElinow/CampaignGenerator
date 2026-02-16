
from NGIN import SimulaeNodeStatus
from NGIN.NGIN_utils.social_scales_utils import random_bell_curve_value
from .NGIN_utils.ngin_utils import *
from .NGIN_utils.social_scales_utils import *
from .NGIN_config.madlibs import *

FAC = 'FAC'
POI = 'POI'
PTY = 'PTY'
LOC = 'LOC'
OBJ = 'OBJ'

NAME = "Name"
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
MEMORY = "Memory"
SCALES = "Scales"

ALL_NODE_TYPES = [FAC,POI,PTY,LOC,OBJ]
NODETYPES = [POI,PTY,LOC,OBJ] # person, people, place, thing
SOCIAL_NODE_TYPES = [FAC,POI,PTY]
GROUP_NODE_TYPES = [FAC,PTY]
PEOPLE_NODE_TYPES = [POI,PTY]
INANIMATE_NODE_TYPES = [LOC,OBJ]

DEFAULT_POLICY_VALUE = 4 # halfway between 1 and 7
DEFAULT_PERSONALITY_VALUE = 3 # halfway between 0 and 6

POLICY_STRENGTH_RANGE = [0, 10] # should match len of SCALE_DEGREE_DESCRIPTORS
PERSONALITY_STRENGTH_RANGE = [0, 10] # should match len of SCALE_DEGREE_DESCRIPTORS

POLICY_DIFFERENTIAL_DESCRIPTORS = [
    "Aligned",             # 0
    "Similar",             # 1
    "Somewhat Similar",    # 2
    "Different",           # 3
    "Very Different",      # 4
    "Near-Opposed",        # 5
    "Opposed",             # 6
]

SOCIAL_DIFFERENTIAL_DESCRIPTORS = [
    "Identical",      # delta 0–4
    "Similar",        # delta 5–14
    "Comparable",     # delta 15–24
    "Distinct",       # delta 25–34
    "Different",      # delta 35–49
    "Contrasting",    # delta 50–64
    "Opposed",        # delta 65–79
]

SCALE_DEGREE_DESCRIPTORS = [
    "",                    # 0 — effectively aligned / indistinguishable
    "Rather ",             # 1
    "Slightly ",           # 2
    "Mildly ",             # 3
    "Moderately ",         # 4
    "Noticeably ",         # 5
    "Significantly ",      # 6
    "Strongly ",           # 7
    "Extremely ",          # 8
    "Diametrically ",      # 9 — categorical divergence
]

class SimulaeNode:

    # id, ntype, refs, attrs, reltn, checks, abilities

    def __init__(self,  given_id=None, 
                        nodetype=OBJ,
                        references: dict[str, Any] | None = None,
                        attributes: dict[str, Any] | None = None,
                        relations: dict[str, Any] | None = None, 
                        checks: dict[str, Any] | None = None, 
                        abilities: dict[str, Any] | None = None,
                        scales: dict[str, dict[str, Any]] | None = None, 
                        memory: list | None = None,):
        '''
        Docstring for __init__
        
        :param self: Description
        :param given_id: String ID for this node. If None, a random UUID will be generated.
        :param nodetype: Type of node (see ALL_NODE_TYPES). Default's to OBJ (object)
        :param references: Dictionary of string-to-string 'references'
        :type references: dict[str, Any] | None
        :param attributes: Dictionary of string-to-number 'attributes'
        :type attributes: dict[str, Any] | None
        :param relations: Dictionary of string-to-node 'relations' describing the physical relationship between this node and any referenced nodes
        :type relations: dict[str, Any] | None
        :param checks: Lookup of this node's status 'checks'
        :type checks: dict[str, bool] | None
        :param abilities: Lookup of this node's abilities, if applicable.
        :type abilities: dict[str, Any] | None
        :param scales: Dictionary of string-to-dictionary 'scales' describing this node's positions on various social/political axes if applicable. 
        :type scales: dict[str, dict[str, Any]] | None
        :param memory: Log of events this node has perceived/experienced, if applicable.
        :type memory: list | None
        '''

        self.ID = given_id if given_id else str(uuid.uuid1())
        
        # avoid mutable default arguments being shared between instances
        if references is None:
            self.References = { NAME: None }
        else:
            self.References = dict(references)

        self.Nodetype = nodetype

        self.Scales = {} if scales is None else dict(scales)

        if self.Nodetype in SOCIAL_NODE_TYPES:
            self.Scales[POLICY] = self.generate_policy()

            if self.Nodetype is POI:
                self.Scales[PERSONALITY] = self.generate_personality()

        self.Attributes = {} if attributes is None else dict(attributes)

        self.Relations = {
            CONTENTS:{ nt:{} for nt in NODETYPES},      # organs for POI, items contained for LOC/OBJ
            COMPONENTS:{ nt:{} for nt in NODETYPES},    # limbs for POI, parts for OBJ
            ATTACHMENTS:{ nt:{} for nt in NODETYPES},    # accessories, clothing, equipped items for POI, attachments for OBJ
            ADJACENT: {} if nodetype != LOC else { nt:{} for nt in NODETYPES} # adjacent locations for LOC
        }

        if relations is not None:
            for k,v in relations.items():
                self.Relations[k] = v
        
        self.Checks = {} if checks is None else dict(checks)
        self.Abilities = {} if abilities is None else dict(abilities)
        self.Memory = memory if memory is not None else []
        
    def keyname(self, *args) -> str:
        return '|'.join(args)
    
    def get_description(self):
        description = ""

        if self.Nodetype == POI:

            associations = self.describe_faction_associations()

            policies = self.describe_political_beliefs()

            personality = self.describe_personality()

            description = "{0}, A {1} year old {2}\n--- ASSOCIATIONS ---\n{3}\n--- PERSONALITY ---\n{4}\n--- POLITICAL BELIEFS ---\n{5}".format(
                self.get_reference(NAME),
                self.get_attribute("Age"),
                self.get_reference("Gender"),
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

    def __str__(self) -> str:
        name = self.get_reference(NAME)

        if name and type(name) == str:
            return name
        
        if self.Nodetype and self.ID:
            return f"{self.Nodetype}({self.ID})"
        
        return ""

    def get_location(self):
        logDebug("get_location()")

        return self.get_reference(LOC)

    def get_adjacent_locations(self: SimulaeNode) -> list[SimulaeNode] | None:
        logDebug("get_adjacent_locations()")
        
        adjacents = self.get_relation(ADJACENT)

        if adjacents:
            return [ node for nid, node in adjacents.items() if node.Nodetype == LOC ] 
        
        return []

    def add_adjacent_location(self, loc, reciprocate=True):
        logDebug("add_adjacent_location(",loc,")")

        # check if loc is already an adjacent location

        if self.has_relation(loc.ID, loc.Nodetype)

        self.add_reference(ADJACENT, loc.ID)
        loc.add_reference(ADJACENT, self.ID, reciprocate=False)


    def knows_about(self, node):
        logDebug("knows_about(",node,")")

        knows_about = False

        if node.Nodetype in SOCIAL_NODE_TYPES:
            if self.has_relation(node, node.Nodetype): # already has relationship
                knows_about = True

        elif node.Nodetype in INANIMATE_NODE_TYPES:
            
            if self.has_relation(node, node.Nodetype): # already has relationship
                knows_about = True

        logDebug("-> ",knows_about)
        return knows_about


    def get_reference(self, key: str) -> str | None:
        logDebug("get_reference(",key,")")
        
        if key in self.References:
            return self.References[key]

        return None

    def set_reference(self, key: str | None, value: str | None):
        logDebug("set_reference(",key,value,")")

        if not key:
            raise ValueError("Reference key cannot be None or empty")
        
        if not value:
            raise ValueError("Reference value cannot be None or empty")

        if not self.References:
            logWarning("References dictionary is None, initializing to empty dict")
            self.References = {}

        self.References[key] = value # type: ignore

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

    def determine_relation(self, node, interaction=None) -> dict | None:
        '''
        Calculates 'Relation' (Physical Relation) between self and given node
        
        :param self: Description
        :param node: Description
        :param interaction: Description
        :return: Description
        :rtype: Literal['Perfectly Aligned']
        '''

        logDebug("determining",self,"(physical) relation to",node)

        relationship = {}

        for relation_type in RELATIVE_TYPES:

            if node.ID in self.Relations[relation_type][node.Nodetype]: # existing relationship found
                relationship = self.Relations[relation_type][node.Nodetype][node.ID]

                return relationship

        # not found
        logWarning("Unhandled relation")

        return None

    def determine_relationship(self, node: SimulaeNode, interaction=None):
        '''
        Calculates 'Relationship' (Social Relation) between self and given node
        
        :param self: Description
        :param node: Description
        :param interaction: Description
        :return: Description
        '''

        logDebug("determining",self,"social relationship with",node)

        relationship = {
            NODETYPE : node.Nodetype,
            STATUS : "new",
            REPUTATION : [0,0],
            INTERACTIONS : []
        }

        if self.has_relationship(node.ID, node.Nodetype): # existing relationship
            relationship = self.Relations[node.ID]

            # update existing relationship ?

            return relationship

        else: # new relationship
            if node.Nodetype in SOCIAL_NODE_TYPES: # other node is a social node

                if self.Nodetype in SOCIAL_NODE_TYPES: # self -> social nodetype

                    for scale in [POLICY_SCALES, PERSONALITY_SCALES]:

                        scale_name: str = scale['name']

                        if scale_name not in self.Scales:
                            logWarning(f"Node {self} missing scale '{scale_name}' for relationship calculation")
                            continue

                        if scale_name not in node.Scales:
                            logWarning(f"Node {node} missing scale '{scale_name}' for relationship calculation")
                            continue

                        self_scale = self.get_scale(scale_name)

                        if not self_scale:
                            logWarning(f"Node {self} has no values for scale '{scale_name}' for relationship calculation")
                            continue

                        node_scale = node.get_scale(scale_name) 

                        if not node_scale:
                            logWarning(f"Node {node} has no values for scale '{scale_name}' for relationship calculation")
                            continue

                        scale_diff = get_scale_diff(
                            master_scale=scale['scales'], 
                            scale=self_scale, 
                            comparison_scale=node_scale,
                            descriptors=scale['descriptors'],
                            descriptors_buckets=scale['descriptors_buckets'],
                            scale_center_index=scale['center_index'])


                    relationship[scale_name] = scale_diff # type: ignore
                    #relationship[POLICY_DISPOSITION] = self.get_policy_disposition( scale_diff[0] )

                    return relationship

                # self -> inanimate nodetype

                return relationship

            elif node.Nodetype in INANIMATE_NODE_TYPES: # other node is an inanimate node
                return relationship
        
    def update_relation(self: SimulaeNode, node: SimulaeNode, interaction=None) -> dict | None:
        '''
        Update the (physical) relation between self and given node
        
        :param self: Description
        :type self: SimulaeNode
        :param node: Description
        :type node: SimulaeNode
        :param interaction: Description
        :return: Description
        :rtype: dict[Any, Any] | None
        '''
        
        logDebug("update_relation(",node,")")
        
        if not node:
            raise ValueError
        
        for relation_type in RELATIVE_TYPES:

            if node.ID in self.Relations[relation_type][node.Nodetype]: # existing relationship found
                relationship = self.Relations[relation_type][node.Nodetype][node.ID]

                determined_relationship = self.determine_relation(node, interaction)

                if determined_relationship:
                    self.Relations[relation_type][node.Nodetype][node.ID] = determined_relationship
                    return determined_relationship

                # no existing relation found 

    def get_relation(self, node) -> dict | None:
        '''
        Returns Physical relation to given node, if known. Otherwise, 'None'
        
        :param self: Description
        :param node: Description
        :return: Description
        '''

        logDebug("get_relation(",node,")")

        if self.has_relation(node.ID, node.Nodetype):
            return self.Relations[node.Nodetype][node.ID]

        return None
    
    def set_relation(self: SimulaeNode, node: SimulaeNode, relation_type: str = CONTENTS):
        logDebug("set_relation(",node,")")

        if not node:
            raise ValueError("Node cannot be None")

        if relation_type not in RELATIVE_TYPES:
            raise ValueError(f"Invalid relation type '{relation_type}'. Must be one of {RELATIVE_TYPES}")

        self.Relations[relation_type][node.Nodetype][node.ID] = relation_type

    def get_relations_by_criteria(self, criteria):
        logDebug("get_relations_by_criteria(",criteria,")")
        
        return [] # TODO AE: implement 
    
    def get_relation_type(self: SimulaeNode, node: SimulaeNode) -> str | None:
        logDebug("get_relation_type(",node,")")

        for relation_type in RELATIVE_TYPES:

            if node.ID in self.Relations[relation_type][node.Nodetype]: # existing relationship found
                return relation_type

    def has_relation( self: SimulaeNode, node_id: str, nodetype: str ): # TODO AE: Reimplement 
        logDebug("has_relation(",node_id,", ",nodetype,")")

        for relation_type in RELATIVE_TYPES:

            if node_id in self.Relations[relation_type][nodetype]: # existing relationship found
                return relation_type
    
    def has_relationship( self: SimulaeNode, key: str, nodetype: str ):
        logDebug("has_relationship(",key,", ",nodetype,")")

        return key in self.Relations.get(nodetype, {})
    
    # Checks Section

    def set_check(self, key: str, value: bool):
        logDebug("set_check(",key,", ",value,")")

        if not key:
            logWarning("Check key cannot be None or empty")
            return

        self.Checks[key] = value

    def has_check(self, key: str) -> bool:
        logDebug("has_check(",key,")")

        if not key:
            return False

        return key in self.Checks

    def get_check(self, key:str):
        logDebug("get_check(",key,")")

        if key in self.Checks:
            return self.Checks[key]
        
        return None

    def remove_check(self, key:str):
        logDebug("remove_check(",key,")")

        if not key:
            logWarning("Check key cannot be None or empty")
            return

        if key in self.Checks:
            del self.Checks[key]

    def generate_policy(self, use_rng: bool = True):
        logDebug("generate_policy()")

        return self.generate_values_for_scales(POLICY_SCALE, scale_strength_range=POLICY_STRENGTH_RANGE, use_rng=use_rng)
        
    def generate_personality(self, use_rng: bool = True) -> dict:
        logDebug("generate_personality()")

        return self.generate_values_for_scales(PERSONALITY_SCALE, scale_strength_range=PERSONALITY_STRENGTH_RANGE, use_rng=use_rng)
    
    def generate_scale(self, 
                        use_rng: bool = True, 
                        scales_name: str = "", 
                        scales: dict[str, list[str]] | None = None, 
                        scales_strength_range: list[int] | None = [0,10]) -> dict:
        logDebug("generate_scale()")

        scales = self.generate_values_for_scales(
            scales=scales,
            scale_strength_range=scales_strength_range, 
            std_dev=None,
            std_dev_variance=1,
            use_rng=use_rng)

        self.Scales[scales_name] = scales
        
        return scales

    def get_scale(self, scale_name: str) -> dict | None:
        if self.Nodetype == POI:

            if scale_name in self.Scales:
                return self.Scales[scale_name]
            
        return None
    
    def get_political_beliefs(self) -> dict | None:
        return self.get_scale(POLICY)

    def get_personality(self) -> dict | None:
        return self.get_scale(PERSONALITY)

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
        
    def policy_diff( self, compare_policy: dict ):
        self_policy = self.get_political_beliefs()
        
        if not self_policy or not compare_policy:
            logWarning("One or both nodes missing political beliefs scale for policy_diff calculation")
            return None
        
        return get_scale_diff( POLICY_SCALE, self_policy, compare_policy, SOCIAL_DIFFERENTIAL_DESCRIPTORS, [3, 5, 8, 13, 21, 34], 3)
    
    def social_diff( self: SimulaeNode, compare_personality: dict):
        self_personality = self.get_personality()

        if not self_personality or not compare_personality:
            logWarning("One or both nodes missing personality scale for social_diff calculation")
            return None

        return get_scale_diff( PERSONALITY_SCALE, self_personality, compare_personality, SOCIAL_DIFFERENTIAL_DESCRIPTORS, [3, 5, 8, 13, 21, 34], 3)

    def get_scale_index(self: SimulaeNode, scale:str, key:str) -> int:
        logDebug("get_scale_index(",scale,", ",key,")")

        if scale not in self.Scales:
            raise ValueError(f"Scale '{scale}' not found in node scales")

        if key not in self.Scales[scale]:
            raise ValueError(f"Key '{key}' not found in scale '{scale}'")

        return self.Scales[scale][key][0] # index is first element of tuple (index, strength)

    def describe_political_beliefs(self):
        logDebug("describe_political_beliefs()")

        summary = ""

        if POLICY not in self.References:
            return ""

        politics = self.References[POLICY]

        if not politics:
            logWarning("No political beliefs scale found in references for node {0}".format(self))
            return ""

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

        personality = self.get_scale(PERSONALITY)

        if not personality:
            logWarning("No personality scale found in references for node {0}".format(self))
            return ""

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

            #d[STATUS] = self.Status.toJSON()

            return d

        except Exception as e:
            print("ERROR WHILE SAVING", type(e), str(e))
            return {}


def simulaenode_from_json(data: dict):
    logDebug("from_json(...)")
    
    try:

        if type(data) != type({}):
            raise ValueError(f"from_json | invalid data type: {type(data)}")

        keys = list(data.keys())

        n_id = data[ID] if str.lower(ID) in keys else None
        n_type = data[NODETYPE] if str.lower(NODETYPE) in keys else None
        n_refs = data[REFERENCES] if str.lower(REFERENCES) in keys else {}
        n_attr = data[ATTRIBUTES] if str.lower(ATTRIBUTES) in keys else {}
        n_rels = data[RELATIONS] if str.lower(RELATIONS) in keys else {}
        n_checks = data[CHECKS] if str.lower(CHECKS) in keys else {}
        n_abilities = data[ABILITIES] if str.lower(ABILITIES) in keys else {}
        n_scales = data[SCALES] if str.lower(SCALES) in keys else {}
        n_memory = data[MEMORY] if str.lower(MEMORY) in keys else []

        if not n_id or not n_type:
            raise ValueError(f"Cannot determine ID or nodetype of entity |\n {data}")

        relations = { nt:{} for nt in ALL_NODE_TYPES }
        for ntype, nodes in n_rels.items():
            logDebug(ntype)
            for nid, ndata in nodes.items():
                node = simulaenode_from_json(ndata)
                
                if node:
                    logDebug(f"-> {node.ID}")
                    relations[ntype][node.ID] = node
                else:
                    logError(f"Failed to parse node with id {nid} and nodetype {ntype} in relations of node with id {n_id}")
                    pass

        n = SimulaeNode(
            given_id=n_id, 
            nodetype=n_type, 
            references=n_refs, 
            attributes=n_attr, 
            relations=relations, 
            checks=n_checks, 
            abilities=n_abilities,
            scales=n_scales,
            memory=n_memory)
    
        return n   

    except Exception as e:
        logError(e)     

    return None


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
