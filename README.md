# CampaignGenerator
	Adaptive and Modular Mission Generator for RPG

## Mission Generator
	mission_generator.py
	NGIN
		generate_element()
			creates a new node with random attributes 
		generate_state( num_nodes )
			generates multiple new random nodes to (re)populate the game-state
		generate_missions()
			Selects (at random) a node in the game-state and randomizes a
                mission based on the available options for the chosen node's
                type and player-disposition
		search()
			returns index of subject (by name and node-type only) necessitated 
				by the inefficient search structure's node organization
		choose_mission()
			To add more interractivity and user-control
                this function will give several available options to allow
                the player to 'control' their actions and interract
                with other nodes in a manner of their choice.
		start()
			Iterates through the game state generating missions based on
                available nodes in the state.
		generate_event()
			Selects a node as event basis, then generates an event based on 
                the node's type. Events are similar to missions, but are
                essentially the mission outcomes of other entities

## Faction Generator
	faction_generator.py
	generate_policy()
		Selects one of each option for each policy 'scale'
            also generates a random weight value to convey the
            importance of that policy to the faction's agenda/members
	politic_diff()
		Gives policy differential score and summary

