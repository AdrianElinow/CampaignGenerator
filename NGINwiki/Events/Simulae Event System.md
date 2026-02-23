The [[Simulae Event System]] is the process by which the [[Simulae NGIN]] propagates the information that is created by a [[Simulae Event]] back into the world model and other [[Simulae Systems]]

### Diagram

```mermaid

flowchart LR

	start["Start"]
	start --> srcs
	srcs["Source(s)"] -- "Attempt Ability" --> cAbility{"Can perform Ability? (Conditions met?)"}
	cAbility -- "No" --> start
	cAbility -- "Yes" --> tEvent["Event Trigger"]
	tEvent --> event["Event"]
	event -- "check if anything was affected" --> cTargets{"Targets affected?"}
	
	cTargets -- "Yes" --> tgts["Affect Target(s)"]
	cTargets -- "No" --> start
	
	event -- "observed by" --> obs["Observer(s)"]
	
	tgts -- "Apply Event Effects" --> tnpc["Target NPC"]
	tnpc -- "Process Experience" --> tnpc_xp["Experience"]
	tnpc_xp -- "Add to Memory" --> tnpc
	
	obs --> obs_npc["Observer NPC"]
	obs_npc -- "Process Experience" --> obs_npc_xp["Experience"]
	obs_npc_xp -- "Add to Memory" --> obs_npc
	
```


