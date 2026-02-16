FAC = 'FAC'
POI = 'POI'
PTY = 'PTY'
LOC = 'LOC'
OBJ = 'OBJ'

NAME = "Name"
ADJACENT = "Adjacent"
STATUS = "Status"
INTERACTIONS = "Interactions"
REPUTATION = "Reputation"

ID = "ID"
REFERENCES = "References"
NODETYPE = "Nodetype"
ATTRIBUTES = "Attributes"

CHECKS = "Checks"
ABILITIES = "Abilities"
MEMORY = "Memory"
SCALES = "Scales"
DISPOSITION_SUFFIX = "Disposition"
POLICY_DISPOSITION = "PolicyDisposition"
SOCIAL_DISPOSITION = "SocialDisposition"

ALL_NODE_TYPES = [FAC,POI,PTY,LOC,OBJ]
PHYSICAL_NODETYPES = [POI,PTY,LOC,OBJ] # person, people, place, thing
SOCIAL_NODE_TYPES = [FAC,POI,PTY]
GROUP_NODE_TYPES = [FAC,PTY]
PEOPLE_NODE_TYPES = [POI,PTY]
INANIMATE_NODE_TYPES = [LOC,OBJ]

RELATIONS = "Relations"
CONTENTS = "Contents"
COMPONENTS = "Components"
ATTACHMENTS = "Attachments"
PHYSICAL_RELATIVE_TYPES = [CONTENTS, COMPONENTS, ATTACHMENTS, ADJACENT]
RELATION_TYPES = PHYSICAL_RELATIVE_TYPES + PHYSICAL_NODETYPES

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

STATUS_THRESHOLDS = "status_thresholds"
THREAT = "threat"
HUNGER = "hunger"
THIRST = "thirst"
DRINK = "drink"
SLEEP = "sleep"
SICK = "sick"
TEMPERATURE = "temperature"
COLD = "cold"
HOT = "hot"
EXHAUSTION = "exhaustion"
LONELINESS = "loneliness"
LOW = "low"
HIGH = "high"
MINIMUM = "min"
MAXIMUM = "max"
VALUE = "value"

STATUS_ATTRIBUTES = [HUNGER, THIRST, HOT, COLD, EXHAUSTION, LONELINESS, SICK]

PRIORITY_MODIFIERS = "priority_modifiers"
CRITICAL_PRIORITY = "critical_priority"
HIGH_PRIORITY = "high_priority"
MEDIUM_PRIORITY = "medium_priority"
LOW_PRIORITY = "low_priority"

TASK_PRIORITIES = [CRITICAL_PRIORITY, HIGH_PRIORITY, MEDIUM_PRIORITY, LOW_PRIORITY]