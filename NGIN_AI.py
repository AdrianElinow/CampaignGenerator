

from SimulaeNode import SimulaeNode

class NGIN_Simulae_Actor(SimulaeNode):

	def __init__(self, simulae_node):
		self.SimulaeNode = simulae_node

	def Turn_RecursiveMinMax(self, ngin_state):
		pass

	def Turn_Random(self, ngin_state, actor):
		pass

	def Turn_StackMinMax(self, ngin_state):

		# 			depth, turn num, state, moves
		action_stack = [ (0, 0, ngin_state, []) ]
	
		best_moves = []
		best_val = 0

		turn_count = get_turn_count(ngin_state)

		while not action_stack:
			depth, turn_index, state, moves = action_stack.pop()

			print('NGIN MinMax Stack Popped: [{0}, {1}, <state>, <moves> : ..,[{2}] ]'.format(depth, turn_index, moves[-1]))

			if is_terminal_state(state) or depth <= 0:
				value = heuristic(state)

				print('heuristic:',value)

				if turn_state is 0: # actors turn
					if value > best_val:
						best_val = value
						best_moves = moves
				
				else:  # non-actor turn
					if value < best_val:
						best_val = value
						best_moves = moves

			else: # not terminal

				# add moves to stack
				next_moves = get_actions( state, self.SimulaeNode )
				next_turn = (turn_index + 1) % turn_count

				for move in next_moves:
					next_move, next_state = move
					action_stack.push( (depth+1, next_turn, next_state, moves + [next_move] ) )

		print('Best Move: {0} -> <{1}>', best_moves[0], best_val)
		print('     Moves: [', ','.join(best_moves) ,']')

		return best_moves[0] # best_action


	def is_terminal_state(state):
		''' End-game state? '''
		is_terminal_state = True

		actors = len(state.relations['FAC'])

		if len(state.relations['POI']) > 0:
			poi_per_actor = [ (actor.id, get_affiliated(state, actor, 'POI')) for actor in actors ]
			
			if not only_one(poi_per_actor): # POIs from multiple Factions still in-play
				is_terminal = False

		elif len(state.relations['PTY']) > 0:
			pty_per_actor = [ (actor.id, get_affiliated(state, actor, 'PTY')) for actor in actors ]
			
			if not only_one(poi_per_actor): # POIs from multiple Factions still in-play
				is_terminal = False

		return is_terminal

	def get_affiliated(state, actor, nodetype):
		return len([ node if node.references['FAC'] == actor.id for node in state.relations[nodetype]])

	def only_one(nt_per_actor):
		has_one = False
		for val in nt_per_actor:
			if val[1] is not 0:
				if has_one:
					return False
				has_one = True

		return has_one


	def get_actions(state, actor):
		
		# TODO : IMPLEMENT

		return []

	def get_turn_count(state):
		''' return number of game actors '''
		return len(state.relations['FAC'])


	def heuristic(ngin_state):
		''' simple end-game state heuristic '''

		points = 0
		# win-state: only actor faction pawns are left
		for nt in NODETYPES:
			points += get_affiliated(state, self.SimulaeNode, nt) * get_nodetype_point_modifier(nt)

		# should return '0' when actor loses in this game-state
		return points

	def get_nodetype_point_modifier(node_type):
		return {
			'POI' : 10,
			'PTY' : 100,
			'LOC' : 500,
			'OBJ' : 5
		}[node_type]


def NGIN_AI_test():
	
	state = SimulaeNode_test()

	actor = NGIN_Simulae_Actor(state.relations['FAC'][0])

	print('Actor:', actor.SimulaeNode.id)

	print('Action:', actor.Turn_StackMinMax(state) )


if __name__ == '__main__':
	print('NGIN_AI | Running tests')

	NGIN_AI_test()
