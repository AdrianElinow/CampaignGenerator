

# NPC socialization

## Policy Scales

```json
POLICY_SCALE = {
    "Economy":          ["Communist", "Socialist", "Interventionist", "Indifferent", "Capitalist", "Free-Capitalist","Hyper-Capitalist"],
    "Liberty":          ["Totalitarian","Authoritarian","Centralized","Indifferent","Liberal","Libertarian","Anarchist"],
    "Class":            ["Under-Class", "Working-Class", "Populist", "Indifferent", "Middle-Class", "Aristocratic", "Plutocratic"],
    "Culture":          ["Reactionary", "Traditionalist", "Conservative", "Indifferent", "Progressive", "Accelerationist","Post-Culturalist"],
    "Diplomacy":        ["Supranationalist", "Globalist", "Diplomatic", "Indifferent", "Patriotic", "Nationalist", "Isolationist"],
    "Militancy":        ["Warhawk","Militarist","Forceful","Indifferent","Conflict-Averse","Nonviolent","Pacifist"],
    "Diversity":        ["Ethnocentrist","Homogenist","Preservationist","Indifferent","Pluralist","Multiculturalist","Inclusionist"],
    "Secularity":       ["Atheist", "Apostate", "Secularist", "Indifferent", "Religious", "Devout", "Fundamentalist"],
    "Technology":       ["Technophobic", "Luddite", "Hesitant", "Indifferent", "Modernist", "TechnoOptimist","Transhumanist"],
    "Legality":         ["Lawless","Arbitrary","Pragmatic","Indifferent","Regulatory","Proceduralist","Legalist"],
    "Justice":          ["Vengeful","Retributive","Punitive","Indifferent","Corrective","Rehabilitative","Abolitionist"],
    "Natural-Balance":  ["Eco-Absolutist","Ecologist","Conservationist","Indifferent","Utilitarian","Productivist","Industrialist"],
    "Government":       ["Popular-Democratic", "Democratic", "Repulican", "Indifferent", "Oligarchic", "Autocratic", "Dictatorial"],
}
```

## Personality Scales

```json
PERSONALITY_SCALE = {
    "Loyalty": ["Rebellious", "Subversive", "Independent", "Indifferent", "Conformist", "Loyal", "Zealous"],
    "Ambition": ["Self-Sabotaging", "Apathetic", "Unmotivated", "Steady", "Driven", "Ambitious", "Messianic"],
    "Empathy": ["Sadistic", "Callous", "Apathetic", "Neutral", "Sympathetic", "Empathetic","Altrustic"],
    "Emotionality": ["Volatile","Reactive","Intense","Neutral","Calm","Flat","Cold"],
    "Risk": ["Risk-Averse", "Guarded", "Cautious", "Balanced", "Adventurous", "Daring", "Reckless"],
    "Conscience": ["Immoral", "Amoral", "Rational", "Pragmatic", "Ethical", "Idealistic", "Virtuous"],
    "Conscientiousness": ["Negligent", "Careless", "Irresponsible", "Neutral", "Reliable", "Conscientious", "Perfectionist"],
    "Curiosity": ["Closed-Minded", "Indifferent", "Interested", "Curious", "Inquisitive", "Investigative", "Obsessive"],
    "Trust": ["Paranoid", "Distrustful", "Skeptical", "Neutral", "Trusting", "Very Trusting", "Gullible"],
    "Resilience": ["Fragile", "Sensitive", "Stressed", "Stable", "Resilient", "Tough", "Unshakeable"],
    "Assertiveness": ["Passive", "Submissive", "Reserved", "Neutral", "Assertive", "Commanding", "Overbearing"],
    "Conflict-Style": ["Avoidant", "Passive-Aggressive", "Diplomatic", "Neutral", "Confrontational", "Aggressive", "Violent"],
    "Humor": ["Dry", "Serious", "Reserved", "Neutral", "Witty", "Joker", "Clownish"],
    "Adaptability": ["Rigid", "Inflexible", "Cautious", "Neutral", "Flexible", "Adaptive", "Fluid"],
    "Attachment": ["Avoidant", "Detached", "Reserved", "Neutral", "Affectionate", "Dependent", "Obsessive"],
    "Cognitive-Style": ["Concrete", "Practical", "Analytical", "Balanced", "Abstract", "Systems-Oriented", "Visionary"],
    "Cooperativeness": ["Contrarian","Competitive","Hard-Nosed","Neutral","Agreeable","Collaborative","Self-Effacing"],
    "Social-Energy": ["Reclusive","Withdrawn","Quiet","Neutral","Sociable","Gregarious","Attention-Seeking"],
}
```


## Derivative Scales



# Socialization

## NonVerbal

NPCs will be able to 'size-up' another NPC based on a number of factors:
1. Physical characteristics
    - Size (height, weight, bodyfat, etc)
    - Hair/Eye/Skin color (based on characteristic relevance)
2. Body Language
    - Reads NPC's action state
    - Relaxed? At-work? Ready for combat? Sneaking around? etc.
3. Clothing
    - Garment type (workwear or fine-suit)
    - Aesthetics (tailoring, color, etc)
    - Quality / Condition (material, tailoring, wear)
    - Association (faction indicators, implied job)
4. Accompanyment
    - Other NPCs in their party/group
5. Location
    - Rich suburb, dark seedy nightclub, etc

## Conversation

### Core Interactions

- OPEN (greet, initiate)
- CLOSE (farewell, withdraw, sever-ties)
- TURN (interrupt, cede, stall)
- TOPIC (change-topic, stay-topic)
- INFORM (claim, disclose, reveal, confess, observe, clarify, retract)
- INQUIRE (ask, probe, challenge)
- STANCE (confirm, deny, agree, disagree, accept, refuse, validate, invalidate)
- INFLUENCE (persuade, dissuade, reassure, pressure, threaten)
- AFFECT (comfort, commiserate, praise, criticize, insult, apologize, joke, complain)
- DIRECT (request, demand, command, task, delegate)
- NEGOTIATE (offer, counteroffer, volunteer)
- BOUNDARY (set-boundary, violate-boundary)
- COORDINATE (rally, organize, promote, demote, resign)
- DECEIVE (mislead, conceal, feign, impersonate, entrap, cover)

### Qualifiers

- Domain
    - Identity
    - Fact
    - Intent
    - Policy
    - Relationship
    - Task
    - Resource
- Polarity
    - pro 
    - anti
    - neutral
- Force
    - low
    - medium
    - high
- Honesty
    - truthful
    - deceptive
    - uncertain
- Visibility?
    - private
    - dyadic
    - public
- Evidence
    - none
    - weak
    - strong
- Emotion
    - calm
    - hostile
    - affirmative
    - fearful
- Authority
    - peer
    - superior
    - subordinate
- Time-Scope
    - immediate
    - ongoing
    - future
    - past

