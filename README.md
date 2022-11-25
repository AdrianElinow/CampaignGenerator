# CampaignGenerator
- Adaptive and Modular Mission Generator for RPG campaign. As a DM resource to dynamically generate new missions given the current game-state

## TODO
1. Implement scenarios, presets, etc. (save/load system)
2. Option to choose from presented mission options
	* Rather than have one presented automatically. 
	* Incorporate mission outcomes in a dynamic manner (mission success vs. failure lead to different outcomes, affecting 
3. Webpage UI/UX (P5.js, PHP?)

## Mission Generator
	SimulaeCampaignGenerator.py
	NGIN
		generate_element()
			creates a new node with random attributes 
		generate_event()
			Selects a node as event basis, then generates an event based on 
	                the node's type. Events are similar to missions, but are
	                essentially the mission outcomes of other entities
		generate_state()
			generates multiple new random nodes to (re)populate the game-state '''
		choose_mission()
			To add more interractivity and user-control
                this function will give several available options to allow
                the player to 'control' their actions and interract
                with other nodes in a manner of their choice.
		user_choice()
			Present user with available options, and allow them to pick
                an option to proceed.
		start()
			Iterates through the game state generating missions based on
                available nodes in the state.
        save()
        	writes the modified state to a json save file

	SimulaeNode
		Structure
			id - unique string identifier
			nodetype 
				FAC - FACtion
				POI - Person Of Interest (VIP, HVT, etc.)
				PTY - ParTY
				OBJ - OBJect / OBJective
				LOC - LOCation
			references 	- str : string relations. Includes identifiers
			attributes 	- str : integer/float relations. Includes stats
			relations  	- str : SimulaeObject relations. 
			checks 	   	- str : Boolean. 
			abilities 	- special meta details
		check_membership()
			check_membership(..., node) checks for specific relations between self and given node
		update_relationship()
			recalculates the political differential between self and given node
		has_relationship()
			check function, reports whether or not self and node are aware of each others policies
		policy_diff()
			returns a report describing the differential between self politics and the given node's
		get_policy_index()
			 simply returns integer value of given policy in its discrete spectrum


## Faction Generator
	faction_generator.py
	generate_policy()
		Selects one of each option for each policy 'scale'
            also generates a random weight value to convey the
            importance of that policy to the faction's agenda/members
	politic_diff()
		Gives policy differential score and summary

