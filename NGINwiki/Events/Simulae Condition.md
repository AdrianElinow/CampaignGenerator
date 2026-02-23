[[Simulae Condition]]s are a data structure which can be used to evaluate prerequisites or requirements to trigger [[Simulae Event]]s

> ex: Condition for checking if a spellcaster has enough mana and the target's armor penetration resistance is lower than the caster's penetration attribute
```json
SimulaeCondition = {
	...
	Conditions: [
		{
			"left": {
				"bind": "source"
				"nodetype": "POI"
				"property": "Attributes",
				"key": "Mana",
				"subkey": None,
			},
			"op": ">=",
			"right": {
				"value": 30
			},
		},
		{
			"left": {
				"bind": "target"
				"nodetype": "POI"
				"property": "Attributes",
				"key": "Armor",
				"subkey": None,
			},
			"op": "<",
			"right": {
				"bind": "source"
				"nodetype": "POI"
				"property": "Attributes",
				"key": "ArmorPenetration",
				"subkey": None,
			},
		}
	]
}
```

## Filtering conditionals

In order to filter collection types, the optional 'filter' property can also be applied and configured with a mini-conditional

```json
...
"left": {
	"binding": "actor",
	"component": "Relations",
	"relation_type": "Contents",
	"nodetype": "OBJ",
	"filter": {
	  "component": "References",
	  "keys": ["Name"],
	  "op": "eq",
	  "value": "Wand"
	},
...
```