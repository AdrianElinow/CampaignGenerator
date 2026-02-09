"""
Conversation System (Natural Flow + Learning) — Minimal, Extensible

Key properties:
- Conversations start via Opportunity + Trigger + Motive - Risk - Stress
- Turn types: PHATIC / FRAMING / DISCLOSURE (only some turns change beliefs)
- Conversation state machine: OPENING -> WARMING -> EXCHANGING -> PROBING -> COOLING -> EXIT
- Each NPC maintains a BeliefRecord per other NPC (perceived traits/policies + uncertainty)
- Disclosure updates mean + reduces variance; Framing updates inferred style; Phatic updates comfort/familiarity

This is a reference implementation you can plug into your sim loop and expand.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Tuple
import math
import random


# ----------------------------
# 1) Basic enums / constants
# ----------------------------

class TurnType(Enum):
    PHATIC = auto()       # small talk / acknowledgements
    FRAMING = auto()      # meta-signals (tone, hedging, moral framing)
    DISCLOSURE = auto()   # reveals a fact / stance / skill / experience


class ConvState(Enum):
    OPENING = auto()
    WARMING = auto()
    EXCHANGING = auto()
    PROBING = auto()
    COOLING = auto()
    EXIT = auto()


class ContextType(Enum):
    CASUAL = auto()
    WORK = auto()
    TENSE = auto()
    INTIMATE = auto()


class OpenerMove(Enum):
    GREET = auto()
    OBSERVE = auto()
    REQUEST = auto()
    OFFER_HELP = auto()
    COMPLAIN = auto()
    JOKE = auto()
    CHALLENGE = auto()
    WARNING = auto()
    INTRODUCE = auto()


class DisclosureCategory(Enum):
    IDENTITY = auto()
    BELIEF = auto()
    VALUE = auto()
    SKILL = auto()
    EXPERIENCE = auto()
    EMOTION = auto()


# ----------------------------
# 2) Utility helpers
# ----------------------------

def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))

def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t

def logistic(x: float) -> float:
    # Smooth probability from score
    return 1.0 / (1.0 + math.exp(-x))

def signed_similarity(a: float, b: float, scale: float = 3.0) -> float:
    """Returns -1..+1 similarity for values in roughly [-scale..+scale]."""
    d = abs(a - b)
    return 1.0 - clamp(d / (2 * scale), 0.0, 1.0) * 2.0  # maps 0->+1, max->-1

def pick_weighted(rng: random.Random, items: List[Tuple[object, float]]):
    total = sum(max(0.0, w) for _, w in items)
    if total <= 0:
        return items[-1][0]
    r = rng.random() * total
    upto = 0.0
    for item, w in items:
        w = max(0.0, w)
        upto += w
        if upto >= r:
            return item
    return items[-1][0]


# ----------------------------
# 3) NPC model
# ----------------------------

@dataclass
class TraitEstimate:
    mean: float = 0.0        # in [-3..+3] by default
    variance: float = 3.0    # higher = more uncertain

@dataclass
class BeliefRecord:
    # How sure I am about my overall model of them
    confidence: float = 0.0  # 0..100

    perceived_personality: Dict[str, TraitEstimate] = field(default_factory=dict)
    perceived_policy: Dict[str, TraitEstimate] = field(default_factory=dict)
    perceived_skills: Dict[str, float] = field(default_factory=dict)  # estimated level 0..10

    trust: float = 0.0       # -100..100
    respect: float = 0.0     # -100..100
    affinity: float = 0.0    # -100..100 (like/dislike)
    threat: float = 0.0      # 0..100

    # lightweight reputation tags
    tags: Dict[str, float] = field(default_factory=dict)  # e.g., {"inconsistent": 0.6}

@dataclass
class RelationshipState:
    familiarity: float = 0.0  # 0..100
    comfort: float = 0.0      # -100..100 (how at ease they feel with each other)
    last_interaction_tick: int = 0

@dataclass
class NPC:
    id: str
    name: str

    # Actual traits/policies used by the sim. Values expected in [-3..+3].
    personality: Dict[str, float]
    policy: Dict[str, float]

    # Skill levels 0..10
    skills: Dict[str, float] = field(default_factory=dict)

    # Dynamic state
    stress: float = 0.0      # 0..100
    energy: float = 50.0     # 0..100

    # One additional scope concept: in-group bias 0..1 (0 universal, 1 extreme tribal)
    # You can derive this from your policy scales if you want; here it is explicit.
    in_group_bias: float = 0.2

    # Per-other models
    beliefs_about: Dict[str, BeliefRecord] = field(default_factory=dict)
    relation_with: Dict[str, RelationshipState] = field(default_factory=dict)

    def get_belief(self, other: "NPC") -> BeliefRecord:
        if other.id not in self.beliefs_about:
            self.beliefs_about[other.id] = BeliefRecord()
        return self.beliefs_about[other.id]

    def get_relation(self, other: "NPC") -> RelationshipState:
        if other.id not in self.relation_with:
            self.relation_with[other.id] = RelationshipState()
        return self.relation_with[other.id]


# ----------------------------
# 4) Conversation primitives
# ----------------------------

@dataclass
class ContextEvent:
    """A trigger that can spark a conversation."""
    kind: str                 # e.g., "arrival", "power_flicker", "task_needed"
    intensity: float = 0.5    # 0..1
    topic_hint: Optional[str] = None


@dataclass
class Utterance:
    speaker_id: str
    listener_id: str
    turn_type: TurnType
    text: str

    # These fields carry simulation meaning:
    framing_signals: Dict[str, float] = field(default_factory=dict)   # inferred style cues
    disclosure: Optional["Disclosure"] = None                         # actual info, if any


@dataclass
class Disclosure:
    category: DisclosureCategory
    # Depending on category, one of these will be filled:
    personality_claim: Optional[Tuple[str, float]] = None  # (trait, value)
    policy_claim: Optional[Tuple[str, float]] = None       # (axis, value)
    skill_claim: Optional[Tuple[str, float]] = None        # (skill, level)
    identity_fact: Optional[str] = None
    experience_fact: Optional[str] = None
    emotion_signal: Optional[float] = None                 # -1..+1 valence for listener reaction
    intensity: float = 0.3                                 # 0..1 disclosure depth


# ----------------------------
# 5) Conversation engine
# ----------------------------

@dataclass
class Conversation:
    a_id: str
    b_id: str
    context: ContextType
    state: ConvState = ConvState.OPENING
    turns: List[Utterance] = field(default_factory=list)
    started_tick: int = 0
    max_turns: int = 10


class ConversationEngine:
    def __init__(self, rng: Optional[random.Random] = None):
        self.rng = rng or random.Random()

    # ---------- Initiation ----------

    def can_converse(self, a: NPC, b: NPC) -> bool:
        # Minimal gating: enough energy, not too stressed
        if a.energy < 5 or b.energy < 5:
            return False
        if a.stress > 95 or b.stress > 95:
            return False
        return True

    def initiation_score(self, a: NPC, b: NPC, trigger: ContextEvent) -> float:
        """
        Higher = more likely A initiates with B.
        Score is mapped through logistic() into a probability.
        """
        rel = a.get_relation(b)
        belief = a.get_belief(b)

        # Motives (simple, derive from a subset of traits if present)
        assertive = a.personality.get("Assertiveness", 0.0)
        curious = a.personality.get("Curiosity", 0.0)
        attachment = a.personality.get("Attachment", 0.0)  # if you keep it in personality; else 0
        conscientious = a.personality.get("Conscientiousness", 0.0)

        motive = (
            0.35 * assertive +
            0.25 * curious +
            0.20 * attachment +
            0.20 * conscientious
        )  # roughly [-1..+1] scale

        # Social risk: low trust, high threat, out-group bias
        # Use perceived ideological affinity (if known) to estimate "in-group distance"
        in_group_distance = clamp(1.0 - (belief.ideal_similarity_hint(a, b)), 0.0, 1.0) if hasattr(belief, "ideal_similarity_hint") else 0.0
        risk = (
            0.012 * max(0.0, -belief.trust) +
            0.010 * belief.threat +
            0.40 * a.in_group_bias * in_group_distance
        )

        # Opportunity & trigger
        opportunity = 0.8  # replace with proximity/attention checks in your sim
        trig = trigger.intensity

        # Stress penalty (more stress -> less likely to start casual talk, unless assertive is high)
        stress_penalty = 0.015 * a.stress - 0.05 * max(0.0, assertive)

        # Familiarity makes initiation easier
        familiarity_bonus = 0.012 * rel.familiarity

        raw = (
            1.2 * opportunity +
            1.0 * trig +
            1.0 * motive +
            familiarity_bonus -
            1.0 * risk -
            stress_penalty
        )

        return raw

    def choose_opener(self, a: NPC, b: NPC, trigger: ContextEvent) -> OpenerMove:
        # Simple heuristic: choose opener based on context and a's traits
        assertive = a.personality.get("Assertiveness", 0.0)
        empathy = a.personality.get("Empathy", 0.0)
        conscientious = a.personality.get("Conscientiousness", 0.0)
        humor = a.personality.get("Humor", 0.0)  # if you keep it; else 0

        options: List[Tuple[OpenerMove, float]] = [
            (OpenerMove.GREET, 1.0),
            (OpenerMove.OBSERVE, 1.2),
            (OpenerMove.INTRODUCE, 0.6),
            (OpenerMove.REQUEST, 0.4 + 0.4 * max(0.0, conscientious)),
            (OpenerMove.OFFER_HELP, 0.3 + 0.4 * max(0.0, empathy)),
            (OpenerMove.JOKE, 0.2 + 0.4 * max(0.0, humor)),
            (OpenerMove.COMPLAIN, 0.2 + 0.2 * max(0.0, a.stress / 100.0)),
            (OpenerMove.CHALLENGE, 0.05 + 0.35 * max(0.0, assertive)),
            (OpenerMove.WARNING, 0.05 + 0.25 * max(0.0, assertive) + 0.2 * trigger.intensity),
        ]

        # Trigger influence
        if trigger.kind in {"arrival", "introduction_needed"}:
            options.append((OpenerMove.INTRODUCE, 1.0))
        if trigger.kind in {"task_needed", "coordination"}:
            options.append((OpenerMove.REQUEST, 1.0))
        if trigger.kind in {"danger", "alarm"}:
            options.append((OpenerMove.WARNING, 1.0))

        return pick_weighted(self.rng, options)

    def opener_text(self, opener: OpenerMove, a: NPC, b: NPC, trigger: ContextEvent) -> str:
        # You will replace this with your setting-specific text generator.
        if opener == OpenerMove.GREET:
            return f"Hey."
        if opener == OpenerMove.OBSERVE:
            return f"Long day?"
        if opener == OpenerMove.INTRODUCE:
            return f"Haven’t seen you around. I’m {a.name}."
        if opener == OpenerMove.REQUEST:
            return f"Got a minute?"
        if opener == OpenerMove.OFFER_HELP:
            return f"Need a hand with anything?"
        if opener == OpenerMove.COMPLAIN:
            return f"This place is wearing me down."
        if opener == OpenerMove.JOKE:
            return f"If this gets any worse, I’m charging admission."
        if opener == OpenerMove.CHALLENGE:
            return f"You always this quiet?"
        if opener == OpenerMove.WARNING:
            return f"Stay sharp. Something’s off."
        return "…"

    def maybe_start_conversation(
        self,
        a: NPC,
        b: NPC,
        trigger: ContextEvent,
        tick: int,
        context: ContextType = ContextType.CASUAL,
        threshold_prob: float = 0.50
    ) -> Optional[Conversation]:
        if not self.can_converse(a, b):
            return None
        score = self.initiation_score(a, b, trigger)
        prob = logistic(score - 1.5)  # tune
        if prob < threshold_prob:
            return None

        opener = self.choose_opener(a, b, trigger)
        convo = Conversation(a_id=a.id, b_id=b.id, context=context, started_tick=tick)
        convo.state = ConvState.OPENING
        convo.turns.append(Utterance(
            speaker_id=a.id,
            listener_id=b.id,
            turn_type=TurnType.PHATIC,
            text=self.opener_text(opener, a, b, trigger),
        ))

        # Apply minimal phatic effects immediately
        self.apply_phatic(a, b, strength=0.08)
        return convo

    # ---------- Turn planning ----------

    def next_state(self, convo: Conversation, a: NPC, b: NPC) -> ConvState:
        # Use familiarity/comfort/trust to progress naturally
        rel_ab = a.get_relation(b)
        rel_ba = b.get_relation(a)
        comfort = (rel_ab.comfort + rel_ba.comfort) / 2.0
        familiarity = (rel_ab.familiarity + rel_ba.familiarity) / 2.0

        if convo.state == ConvState.OPENING:
            return ConvState.WARMING
        if convo.state == ConvState.WARMING:
            return ConvState.EXCHANGING if familiarity > 5 or comfort > -10 else ConvState.WARMING
        if convo.state == ConvState.EXCHANGING:
            # Move into probing only if trust or comfort is decent
            trust = (a.get_belief(b).trust + b.get_belief(a).trust) / 2.0
            if trust > -10 and comfort > -20 and familiarity > 12:
                return ConvState.PROBING
            return ConvState.EXCHANGING
        if convo.state == ConvState.PROBING:
            # If stress rises or comfort dips, cool down
            if a.stress > 70 or b.stress > 70 or comfort < -30:
                return ConvState.COOLING
            # Otherwise, after enough turns, cool down
            if len(convo.turns) >= max(6, convo.max_turns - 2):
                return ConvState.COOLING
            return ConvState.PROBING
        if convo.state == ConvState.COOLING:
            return ConvState.EXIT
        return ConvState.EXIT

    def choose_turn_type(self, speaker: NPC, listener: NPC, convo: Conversation) -> TurnType:
        """
        Natural ratios:
          - PHATIC dominates early & cooling
          - FRAMING moderate mid
          - DISCLOSURE gated and rare
        """
        rel = speaker.get_relation(listener)
        belief = speaker.get_belief(listener)

        familiarity = rel.familiarity
        comfort = rel.comfort
        trust = belief.trust
        stress = speaker.stress

        # Base weights by state
        if convo.state in {ConvState.OPENING}:
            w = {TurnType.PHATIC: 1.0, TurnType.FRAMING: 0.1, TurnType.DISCLOSURE: 0.0}
        elif convo.state in {ConvState.WARMING}:
            w = {TurnType.PHATIC: 1.0, TurnType.FRAMING: 0.4, TurnType.DISCLOSURE: 0.1}
        elif convo.state in {ConvState.EXCHANGING}:
            w = {TurnType.PHATIC: 0.9, TurnType.FRAMING: 0.6, TurnType.DISCLOSURE: 0.25}
        elif convo.state in {ConvState.PROBING}:
            w = {TurnType.PHATIC: 0.5, TurnType.FRAMING: 0.6, TurnType.DISCLOSURE: 0.6}
        elif convo.state in {ConvState.COOLING, ConvState.EXIT}:
            w = {TurnType.PHATIC: 1.0, TurnType.FRAMING: 0.2, TurnType.DISCLOSURE: 0.05}
        else:
            w = {TurnType.PHATIC: 1.0, TurnType.FRAMING: 0.3, TurnType.DISCLOSURE: 0.1}

        # Disclosure gating: familiarity + comfort + trust - stress - in_group distance
        in_group_distance = self.estimate_in_group_distance(speaker, listener)
        disclosure_gate = (
            0.02 * familiarity +
            0.02 * (comfort / 10.0) +
            0.02 * (trust / 10.0) -
            0.015 * (stress / 10.0) -
            0.8 * speaker.in_group_bias * in_group_distance
        )
        disclosure_multiplier = clamp(logistic(disclosure_gate) * 1.4, 0.0, 1.25)
        w[TurnType.DISCLOSURE] *= disclosure_multiplier

        # If stress is high, framing and phatic dominate; disclosures less likely
        if stress > 75:
            w[TurnType.DISCLOSURE] *= 0.3
            w[TurnType.FRAMING] *= 1.2

        return pick_weighted(self.rng, [(k, v) for k, v in w.items()])

    def estimate_in_group_distance(self, speaker: NPC, listener: NPC) -> float:
        """
        0..1 distance estimate between speaker and listener based on current perceived policy overlap.
        If speaker doesn't know listener yet, distance ~0.5.
        """
        br = speaker.get_belief(listener)
        if not br.perceived_policy:
            return 0.5

        # Compare speaker's actual policy to perceived listener policy
        sims = []
        for axis, speaker_val in speaker.policy.items():
            est = br.perceived_policy.get(axis)
            if est is None:
                continue
            sims.append((signed_similarity(speaker_val, est.mean), est.variance))
        if not sims:
            return 0.5

        # Similarity in [-1..+1], convert to distance
        avg_sim = sum(s for s, _ in sims) / len(sims)
        return clamp((1.0 - avg_sim) / 2.0, 0.0, 1.0)

    # ---------- Turn content generation ----------

    def generate_turn(self, speaker: NPC, listener: NPC, convo: Conversation) -> Utterance:
        ttype = self.choose_turn_type(speaker, listener, convo)

        if ttype == TurnType.PHATIC:
            text = self.generate_phatic_line(speaker, listener, convo)
            return Utterance(speaker.id, listener.id, ttype, text)

        if ttype == TurnType.FRAMING:
            text, signals = self.generate_framing_line(speaker, listener, convo)
            return Utterance(speaker.id, listener.id, ttype, text, framing_signals=signals)

        # DISCLOSURE
        disclosure = self.generate_disclosure(speaker, listener, convo)
        text = self.render_disclosure_text(speaker, listener, disclosure, convo)
        return Utterance(speaker.id, listener.id, ttype, text, disclosure=disclosure)

    def generate_phatic_line(self, speaker: NPC, listener: NPC, convo: Conversation) -> str:
        # Lightweight conversational glue. No “facts”.
        options = [
            "Yeah.",
            "Mm.",
            "Fair.",
            "I hear you.",
            "It is what it is.",
            "Guess so.",
            "Right.",
            "No kidding.",
            "That’s rough.",
            "Could be worse.",
        ]
        # A little context flavor
        if convo.context == ContextType.WORK:
            options += ["Back to it.", "We’ll get it done.", "Let’s keep moving."]
        if convo.context == ContextType.TENSE:
            options += ["Keep your voice down.", "Not here.", "Eyes open."]
        return self.rng.choice(options)

    def generate_framing_line(self, speaker: NPC, listener: NPC, convo: Conversation) -> Tuple[str, Dict[str, float]]:
        """
        Framing lines reveal style, not explicit beliefs.
        We output "signals" that the listener uses to update perceived personality.
        """
        emotionality = speaker.personality.get("Emotionality", 0.0)
        assertiveness = speaker.personality.get("Assertiveness", 0.0)
        conscientious = speaker.personality.get("Conscientiousness", 0.0)
        trust = speaker.personality.get("Trust", 0.0)

        # Simple line selection keyed by traits
        signals: Dict[str, float] = {}

        if assertiveness > 1.0:
            line = self.rng.choice(["Look—", "Here’s the thing.", "Let’s be clear."])
            signals["Assertiveness"] = +0.25
        elif trust < -1.0:
            line = self.rng.choice(["Maybe.", "Hard to say.", "Depends who’s asking."])
            signals["Trust"] = -0.20
        elif conscientious > 1.0:
            line = self.rng.choice(["We should do it properly.", "Details matter.", "There’s a right way."])
            signals["Conscientiousness"] = +0.20
        elif emotionality > 1.0:
            line = self.rng.choice(["I’m not thrilled about it.", "It gets under my skin.", "I’m tired of this."])
            signals["Emotionality"] = +0.20
        else:
            line = self.rng.choice(["I don’t know.", "Maybe you’re right.", "Could be."])
            signals["Emotionality"] = -0.05  # mild calm/flat inference

        return line, signals

    def generate_disclosure(self, speaker: NPC, listener: NPC, convo: Conversation) -> Disclosure:
        """
        Pick one disclosure category and content.
        Keep it small; early conversations should mostly reduce uncertainty.
        """
        rel = speaker.get_relation(listener)
        comfort = rel.comfort
        familiarity = rel.familiarity

        # Candidate disclosure categories by context and comfort
        weights: List[Tuple[DisclosureCategory, float]] = [
            (DisclosureCategory.SKILL, 0.7),
            (DisclosureCategory.EXPERIENCE, 0.45),
            (DisclosureCategory.BELIEF, 0.35),
            (DisclosureCategory.VALUE, 0.25),
            (DisclosureCategory.IDENTITY, 0.20),
            (DisclosureCategory.EMOTION, 0.25),
        ]
        if convo.context == ContextType.INTIMATE:
            weights = [(c, w * (1.3 if c in {DisclosureCategory.EXPERIENCE, DisclosureCategory.IDENTITY, DisclosureCategory.EMOTION} else 0.9))
                       for c, w in weights]
        if comfort < -20:
            weights = [(c, w * (0.6 if c in {DisclosureCategory.EXPERIENCE, DisclosureCategory.IDENTITY} else 1.0))
                       for c, w in weights]

        cat = pick_weighted(self.rng, weights)

        # intensity grows with familiarity and comfort
        intensity = clamp(0.15 + 0.004 * familiarity + 0.002 * max(0.0, comfort), 0.15, 0.85)

        if cat == DisclosureCategory.SKILL and speaker.skills:
            skill = self.rng.choice(list(speaker.skills.keys()))
            level = speaker.skills[skill]
            return Disclosure(category=cat, skill_claim=(skill, level), intensity=intensity)

        if cat == DisclosureCategory.BELIEF and speaker.policy:
            axis = self.rng.choice(list(speaker.policy.keys()))
            val = speaker.policy[axis]
            return Disclosure(category=cat, policy_claim=(axis, val), intensity=intensity)

        if cat == DisclosureCategory.VALUE and speaker.personality:
            # “Value” here is still a trait claim; in a richer model this would be morality/justice/etc.
            trait = self.rng.choice(list(speaker.personality.keys()))
            val = speaker.personality[trait]
            return Disclosure(category=cat, personality_claim=(trait, val), intensity=intensity)

        if cat == DisclosureCategory.IDENTITY:
            # placeholder identity facts; swap with your life-history system
            facts = [
                "I wasn’t always here.",
                "I grew up on the edge of town.",
                "My family kept their heads down.",
                "I learned early to watch my back.",
            ]
            return Disclosure(category=cat, identity_fact=self.rng.choice(facts), intensity=intensity)

        if cat == DisclosureCategory.EXPERIENCE:
            exps = [
                "I’ve seen things go bad fast.",
                "I lost people the last time this place broke.",
                "I used to work nights when everything was falling apart.",
                "I’ve had to make ugly choices before.",
            ]
            return Disclosure(category=cat, experience_fact=self.rng.choice(exps), intensity=intensity)

        # EMOTION
        # valence: -1..+1; positive indicates warmth/relief, negative indicates bitterness/anger
        emotionality = speaker.personality.get("Emotionality", 0.0)
        valence = clamp((self.rng.random() * 2 - 1) * (0.35 + 0.15 * abs(emotionality)), -1.0, 1.0)
        return Disclosure(category=DisclosureCategory.EMOTION, emotion_signal=valence, intensity=intensity)

    def render_disclosure_text(self, speaker: NPC, listener: NPC, d: Disclosure, convo: Conversation) -> str:
        if d.category == DisclosureCategory.SKILL and d.skill_claim:
            skill, lvl = d.skill_claim
            if lvl >= 7:
                return f"I’m pretty good at {skill}."
            if lvl >= 4:
                return f"I’ve done some {skill}."
            return f"I can handle basic {skill}."

        if d.category == DisclosureCategory.BELIEF and d.policy_claim:
            axis, val = d.policy_claim
            # keep it vague; avoid doctrine dumps
            if val > 1.5:
                return f"I lean hard on the {axis} side."
            if val < -1.5:
                return f"I’m pretty skeptical about {axis}, honestly."
            return f"I’m mixed on {axis}."

        if d.category == DisclosureCategory.VALUE and d.personality_claim:
            trait, val = d.personality_claim
            if val > 1.5:
                return f"I tend to be {trait.lower()}."
            if val < -1.5:
                return f"I’m not exactly known for {trait.lower()}."
            return f"I’m somewhere in the middle on {trait.lower()}."

        if d.category == DisclosureCategory.IDENTITY and d.identity_fact:
            return d.identity_fact

        if d.category == DisclosureCategory.EXPERIENCE and d.experience_fact:
            return d.experience_fact

        if d.category == DisclosureCategory.EMOTION and d.emotion_signal is not None:
            if d.emotion_signal > 0.4:
                return "…I’m glad you get it."
            if d.emotion_signal < -0.4:
                return "…It still makes me angry."
            return "…It’s complicated."

        return "…"

    # ---------- Applying turn effects ----------

    def apply_turn_effects(self, speaker: NPC, listener: NPC, utt: Utterance) -> None:
        """
        Updates listener's beliefs and relationship state based on the turn.
        """
        if utt.turn_type == TurnType.PHATIC:
            self.apply_phatic(speaker, listener, strength=0.06)
            return

        if utt.turn_type == TurnType.FRAMING:
            self.apply_framing(speaker, listener, utt.framing_signals, strength=0.22)
            return

        if utt.turn_type == TurnType.DISCLOSURE and utt.disclosure is not None:
            self.apply_disclosure(speaker, listener, utt.disclosure)
            return

    def apply_phatic(self, speaker: NPC, listener: NPC, strength: float) -> None:
        # Familiarity and comfort drift upward slightly if not already hostile
        rel = speaker.get_relation(listener)
        rel.familiarity = clamp(rel.familiarity + 2.0 * strength, 0.0, 100.0)
        # Comfort responds to the other party's trust (if low trust, small talk can still be awkward)
        br = speaker.get_belief(listener)
        comfort_delta = 10.0 * strength * (0.4 + 0.6 * clamp((br.trust + 100) / 200.0, 0.0, 1.0))
        rel.comfort = clamp(rel.comfort + comfort_delta, -100.0, 100.0)
        # Tiny stress reduction for both
        speaker.stress = clamp(speaker.stress - 2.0 * strength, 0.0, 100.0)
        listener.stress = clamp(listener.stress - 1.0 * strength, 0.0, 100.0)

    def apply_framing(self, speaker: NPC, listener: NPC, signals: Dict[str, float], strength: float) -> None:
        """
        Listener updates perceived personality (small mean drift, variance reduction).
        """
        br = listener.get_belief(speaker)
        rel = listener.get_relation(speaker)

        for trait, signal in signals.items():
            est = br.perceived_personality.setdefault(trait, TraitEstimate(mean=0.0, variance=3.0))
            # shift mean a bit toward inferred direction
            est.mean = clamp(est.mean + signal * strength, -3.0, 3.0)
            # reduce variance slightly as we observe style
            est.variance = clamp(est.variance * (1.0 - 0.03 * strength), 0.5, 5.0)

        # Comfort changes a bit based on listener's own preferences
        listener_empathy = listener.personality.get("Empathy", 0.0)
        # More empathic listeners tolerate framing better
        rel.comfort = clamp(rel.comfort + 6.0 * strength * (0.5 + 0.25 * listener_empathy), -100.0, 100.0)

        # Confidence increases slowly
        br.confidence = clamp(br.confidence + 1.5 * strength, 0.0, 100.0)

    def apply_disclosure(self, speaker: NPC, listener: NPC, d: Disclosure) -> None:
        br = listener.get_belief(speaker)
        rel = listener.get_relation(speaker)

        # Credibility: depends on listener skepticism, speaker trustworthiness signal, and contradiction history
        listener_skepticism = -listener.personality.get("Trust", 0.0)  # higher means more skeptical
        base_cred = 0.75 - 0.08 * listener_skepticism
        base_cred = clamp(base_cred, 0.25, 0.95)

        # If speaker already tagged inconsistent, credibility drops
        incons = br.tags.get("inconsistent", 0.0)
        cred = clamp(base_cred * (1.0 - 0.4 * incons), 0.10, 0.95)

        # Common side-effects: disclosure increases familiarity and shifts trust/affinity modestly
        rel.familiarity = clamp(rel.familiarity + 6.0 * d.intensity, 0.0, 100.0)
        rel.comfort = clamp(rel.comfort + 8.0 * d.intensity * (0.5 + 0.5 * clamp((br.trust + 100) / 200.0, 0.0, 1.0)), -100.0, 100.0)

        # Update content
        if d.personality_claim:
            trait, val = d.personality_claim
            self._belief_update_trait(br.perceived_personality, trait, val, strength=d.intensity, credibility=cred)

            # trust/affinity shifts based on trait agreement (soft)
            if trait in listener.personality:
                sim = signed_similarity(listener.personality[trait], val)
                br.affinity = clamp(br.affinity + 8.0 * d.intensity * sim, -100.0, 100.0)

        if d.policy_claim:
            axis, val = d.policy_claim
            self._belief_update_trait(br.perceived_policy, axis, val, strength=d.intensity, credibility=cred)

            # ideological affinity shift
            if axis in listener.policy:
                sim = signed_similarity(listener.policy[axis], val)
                br.idealogical_affinity_set(sim, d.intensity) if hasattr(br, "idealological_affinity_set") else None
                br.affinity = clamp(br.affinity + 10.0 * d.intensity * sim * (0.6 + 0.4 * (1.0 - listener.in_group_bias)), -100.0, 100.0)
                br.respect = clamp(br.respect + 6.0 * d.intensity * (0.2 + 0.8 * max(0.0, sim)), -100.0, 100.0)

        if d.skill_claim:
            skill, lvl = d.skill_claim
            br.perceived_skills[skill] = lerp(br.perceived_skills.get(skill, 0.0), lvl, 0.6 * d.intensity * cred)
            # competence tends to increase respect
            br.respect = clamp(br.respect + 12.0 * d.intensity * clamp(lvl / 10.0, 0.0, 1.0), -100.0, 100.0)

        if d.identity_fact:
            # identity facts mostly boost trust modestly; also reduce uncertainty broadly
            br.trust = clamp(br.trust + 8.0 * d.intensity * cred, -100.0, 100.0)

        if d.experience_fact:
            # experiences can boost affinity via empathy
            listener_empathy = listener.personality.get("Empathy", 0.0)
            br.affinity = clamp(br.affinity + 8.0 * d.intensity * cred * (0.6 + 0.25 * listener_empathy), -100.0, 100.0)
            # volatile listeners may feel threatened by "ugly choices"
            listener_emotionality = listener.personality.get("Emotionality", 0.0)
            br.threat = clamp(br.threat + 6.0 * d.intensity * max(0.0, listener_emotionality - 1.0), 0.0, 100.0)

        if d.emotion_signal is not None:
            # valence affects affinity strongly, trust moderately
            br.affinity = clamp(br.affinity + 15.0 * d.intensity * d.emotion_signal, -100.0, 100.0)
            br.trust = clamp(br.trust + 7.0 * d.intensity * (1.0 if d.emotion_signal > 0 else -0.5), -100.0, 100.0)

        # Contradiction detection: compare new claims against previous estimates
        contradiction = self._detect_contradiction(br, d)
        if contradiction > 0.0:
            # Drop confidence and trust; add "inconsistent" tag
            br.confidence = clamp(br.confidence - 6.0 * contradiction, 0.0, 100.0)
            br.trust = clamp(br.trust - 10.0 * contradiction, -100.0, 100.0)
            br.tags["inconsistent"] = clamp(br.tags.get("inconsistent", 0.0) + 0.15 * contradiction, 0.0, 1.0)
            # Speaker stress rises if their story is challenged by context (simulated here as contradiction penalty)
            speaker.stress = clamp(speaker.stress + 5.0 * contradiction * d.intensity, 0.0, 100.0)

        # Overall confidence improves from disclosure (unless contradiction cancels it)
        br.confidence = clamp(br.confidence + 4.0 * d.intensity * cred, 0.0, 100.0)

    def _belief_update_trait(
        self,
        space: Dict[str, TraitEstimate],
        key: str,
        claimed_value: float,
        strength: float,
        credibility: float,
        max_scale: float = 3.0,
    ) -> None:
        est = space.setdefault(key, TraitEstimate(mean=0.0, variance=3.0))
        # Update mean toward claim; stronger if low variance and credible
        # "Bayesian-lite": step size inversely proportional to variance
        step = (0.35 * strength * credibility) * (1.0 / max(0.7, est.variance))
        est.mean = clamp(lerp(est.mean, claimed_value, step), -max_scale, max_scale)
        # Reduce variance as info accumulates
        est.variance = clamp(est.variance * (1.0 - 0.18 * strength * credibility), 0.25, 5.0)

    def _detect_contradiction(self, br: BeliefRecord, d: Disclosure) -> float:
        """
        Returns 0..1 contradiction magnitude if new claim deviates sharply from previous estimate.
        """
        if d.policy_claim:
            axis, val = d.policy_claim
            est = br.perceived_policy.get(axis)
            if est and est.variance < 2.0:
                delta = abs(val - est.mean)
                return clamp((delta - 1.5) / 3.0, 0.0, 1.0)  # 1.5 is tolerance
        if d.personality_claim:
            trait, val = d.personality_claim
            est = br.perceived_personality.get(trait)
            if est and est.variance < 2.0:
                delta = abs(val - est.mean)
                return clamp((delta - 1.5) / 3.0, 0.0, 1.0)
        return 0.0

    # ---------- Running a conversation ----------

    def run_conversation(self, convo: Conversation, npc_by_id: Dict[str, NPC]) -> Conversation:
        a = npc_by_id[convo.a_id]
        b = npc_by_id[convo.b_id]

        # If there is already one opener line, continue alternating.
        speaker = b if convo.turns and convo.turns[-1].speaker_id == a.id else a
        listener = a if speaker is b else b

        while convo.state != ConvState.EXIT and len(convo.turns) < convo.max_turns:
            convo.state = self.next_state(convo, a, b)

            if convo.state == ConvState.EXIT:
                break

            utt = self.generate_turn(speaker, listener, convo)
            convo.turns.append(utt)
            self.apply_turn_effects(speaker, listener, utt)

            # Basic energy costs
            speaker.energy = clamp(speaker.energy - 1.5, 0.0, 100.0)
            listener.energy = clamp(listener.energy - 0.5, 0.0, 100.0)

            # Swap
            speaker, listener
