# CampaignGenerator
- Adaptive and Modular Mission Generator for RPG campaign. As a DM resource to dynamically generate new missions given the current game-state

# To start API-server & Client

1. Start the `run_api` script
2. Start the `start_nginclient` script
3. Open a browser to the local server page

# To start the terminal client

1. Start the `generate_campaign` script

## TODO
1. Implement existing faction generator into main NGIN world-gen
	* also add better POI and LOC generation
2. Implement mission outcomes
	* Incorporate mission outcomes in a dynamic manner (mission success vs. failure lead to different outcomes, affecting actor node, gamestate, etc)
3. Add simple AI to non-actor node.
	* Lvl 1: Actor nodes perform random available action
	* Lvl 2: Actor nodes perform action based on minmax algo with limited plan-depth (intelligence attribute), according to randomized goal
	* Lvl 3: Actor nodes perform action based on minmax algo with lengthy plan-depth (intelligence attribute) based on randomized goal
	* Lvl 4: Actor node performs action based on minmax algo with unlimited plan depth based on task-breakdown goal
4. Better non-Actor Simulae AI 
	* goal-oriented task-breakdown Sims AI
6. Webpage UI/UX -> Implement NGIN into Website Project (Django+React)

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

