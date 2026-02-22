
from __future__ import annotations

from dataclasses import dataclass, field
import copy
import uuid
from typing import Any
from .NGIN_utils import get_unique_strs, normalize_str
from .SimulaeEvent import SimulaeEvent

EVENT_CLASSES = ("physical", "social", "internal", "system")
EVENT_VISIBILITIES = ("public", "private", "dyadic")


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

class SimulaeSocialEvent(SimulaeEvent):
    
    def __init__(self, 
                event_type: str, 
                event_subtype: str | None = None, 
                **kwargs):

        event_type = normalize_str(event_type)
        event_subtype = normalize_str(event_subtype)

        super().__init__(
            event_class='social',
            event_type=event_type,
            event_subtype=event_subtype,
            **kwargs
        )

class MemoryEvent(SimulaeEvent):
    
    def from_social_event(self, social_event: SimulaeSocialEvent):
        pass