
from typing import Any, Literal


TruthStatus = Literal["unverified", "believed", "disbelieved", "unknown"]

class Claim:
    id: str
    t_first: int
    t_last: int

    subject: str                        # what the claim is about
    predicate: str                      # "attacked_by", "is_corrupt", "policy_changed", "is_trait", etc.
    obj: Any                            # EntityId, place, number, or structured value

    provenance: list[str]               # events that asserted/implied this
    sources: set[str]                   # who has claimed it (or originated it)

    confidence: float                   # 0..1 how much NPC believes it
    status: TruthStatus                 # believed/unverified/etc.

    volatility: float = 0.5             # 0..1 how quickly this can change (news > biography)
    sensitivity: float = 0.5            # 0..1 how risky it is to repeat
    decay_rate: float = 0.01            # how fast confidence decays without reinforcement
