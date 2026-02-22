A task is an individual unit of a [[Plan]] or a standalone action to be performed by a [[Simulae Actor]]

A task has a few important components:
- A goal state to be achieved
- An action (or sequence of actions) that must be performed to achieve the goal-state

```json
Task = {
	"id": "...",
	"type": "command|quest|contract|objective",
	"parent": "...",
	"issuance": (Event),
	"status": "..."
	"success_conditions": [...],
	"fail_conditions": [...],
	"success_outcomes": [...],
	"fail_outcomes": [...],
	"side_effects": {...},
	"deadline": (Timestamp),
}
```



