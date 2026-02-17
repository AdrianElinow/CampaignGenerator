





from pprint import pprint


class SocialEvent:
    def __init__(self):
        pass







class MemoryEvent:
    def __init__(self, id, ):
        pass




SOCIAL_INTERACTION_TYPES = [
    "Open",
    "Close",
    "Turn",
    "Topic",
    "Inform",
    "Inquire",
    "Stance",
    "Influence",
    "Affect",
    "Direct",
    "Negotiate",
    "Boundary",
    "Coordinate",
    "Deceive",
]

SOCIAL_INTERACTION_QUALIFIERS = {
    "Domain": [
        "Identity",
        "Fact",
        "Intent",
        "Policy",
        "Relationship",
        "Task",
        "Resource"
    ],
    "Polarity": [
        "Positive",
        "Negative",
        "Neutral"
    ],
    "Force": [
        "High",
        "Medium",
        "Low"
    ],
    "Honesty": [
        "Truthful",
        "Deceptive",
        "Neutral"
    ],
    "Visibility": [
        "Public",
        "Private",
        "Dyadic"
    ],
    "Evidence": [
        "None",
        "Weak",
        "Strong"
    ],
    "Authority": [
        "Peer",
        "Superior",
        "Subordinate",
        "None",
    ],
    "Time": [
        "Past",
        "Present",
        "Ongoing",
        "Future"
    ]
}


RESPONSE_WEIGHTS = { interaction_type: { qualifier: { factor: 1.0 for factor in qualifying_factors } for qualifier, qualifying_factors in SOCIAL_INTERACTION_QUALIFIERS.items() } for interaction_type in SOCIAL_INTERACTION_TYPES }
