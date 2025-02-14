

from NGIN.SimulaeNode import *

from queue import PriorityQueue
from queue import Empty as EmptyQueueError

class NGIN_Simulae_Actor(SimulaeNode):

    def __init__(self, simulae_node):
        self.SimulaeNode = simulae_node

        self.inventory = {}
        self.priorities = PriorityQueue()


    def problem_solve(self):
        
        actions = []

        self.prioritize()

        #while not self.priorities.empty():
        #    print(self.priorities.get(timeout=1))


        while not actions:

            try:
                priorities = self.priorities.get(timeout=1)
            except EmptyQueueError:
                return []

            if priorities:
                goal = priorities[1]

                actions = self.get_actions_for_goal(goal)

        return actions


    def get_actions_for_goal(self, goal, action=None):

        goal_type = type(goal)

        if goal_type == type(SimulaeNode):

            if goal.node_type == LOC:
                return self.pathfind_to(goal)
            elif goal.node_type == OBJ:
                return self.acquire(goal)
            elif goal.node_type == POI:
                return self.pathfind_to(goal)
            else:
                return []

        elif goal_type == type(""):

            if goal == "hunger":
                return self.consume('edible')
            elif goal == 'drink':
                return self.consume('drinkable')
            elif goal == 'sleep':
                return self.perform_action(goal)
            elif goal == 'socialize':
                return self.perform_action(goal)
            else:
                print("dont know how to resolve goal: ",goal)

    def prioritize(self):
        priorities = PriorityQueue()

        # Safety & Security needs

        if self.is_threatened():
            priorities.put((0, self.get_prioritized_threats()))

        # Physiological needs
        if self.is_hungry():
            priorities.put((1, 'hunger'))

        if self.is_thirsty():
            priorities.put((2,'drink'))

        if self.is_sleepy():
            priorities.put((3, 'sleep'))

        # Social needs
        if self.needs_socialization():
            priorities.put((4,'socialize'))

        # short-term goals

        goals = self.get_prioritized_short_term_goals()
        for goal in goals:
            priorities.put(goal)

        # long-term goals

        goals = self.get_prioritized_long_term_goals()
        for goal in goals:
            priorities.put(goal)

        self.priorities = priorities
        return priorities


    def get_prioritized_long_term_goals(self):
        # todo AE : impelement
        return []

    def get_prioritized_short_term_goals(self):
        # todo AE : impelement
        return []

    def needs_socialization(self):

        socialization = self.SimulaeNode.get_attribute('social')
        if socialization is not None and socialization <= 50:
            return True

        return False


    def is_sleepy(self):

        exhaustion = self.SimulaeNode.get_attribute('exhaustion')
        if exhaustion is not None and exhaustion >= 60:
            return True

        return False

    def is_thirsty(self):

        thirst = self.SimulaeNode.get_attribute('thirst')
        if thirst is not None and thirst <= 40:
            return True

        return False


    def is_hungry(self):

        hunger = self.SimulaeNode.get_attribute('hunger')
        if hunger is not None:
            if hunger <= 20:
                return True

        return False

    def is_threatened(self):
        # todo AE : impelement
        return False

    def get_prioritized_threats(self):
        # todo AE : impelement
        return []

    def pathfind_to(self, target) -> List:
        # todo AE : impelement
        return [ ("goto",target) ]


    def perform_action(self, target) -> List:

        return [('use',target)]

    def consume(self, consumable) -> List:

        if type(consumable) == type(""):

            item = self.has_vague(consumable, OBJ)

            if item:
                return [('use',item)]
            else:
                return self.acquire(consumable)
                    

        elif type(consumable) == type(SimulaeNode): # handle SimulaeNode
            # todo AE : impelement

            if self.has_node(consumable):
                return [('use',consumable)]
            else:
                return self.acquire(consumable)

    def has_vague(self, target:str, nodetype:str) -> SimulaeNode:

        if type(target) != type(""):
            return None

        if target in self.inventory[nodetype]:
            return True
        else:
            for nid, n in self.inventory[nodetype].items():
                check = n.get_check(target)
                if check:
                    return n

        return False

    def has_node(self, target:SimulaeNode) -> SimulaeNode:

        if type(target) == type(""):
            return None

        # todo ae : implement SimulaeNode inventory
        if target.id in self.inventory[target.nodetype]:
            return target

        return None

    def can_make(self, target):
        # todo AE : impelement
        return False


    def get_recipe(target):
        # todo AE : implement
        return (None, None)

    def acquire(self, target):
  
        #if type(target) == type(""):
        #    print("cant plan to acquire vague",target)
        #    return []

        # do we already have one?
        if self.has_node(target) or self.has_vague(target, OBJ):
            return [] # base case -> already have it
        
        actions = []
        heuristics = {}

        # do we own any? 
        #   if not, same as below, but add 'requires-permission'
        if self.SimulaeNode.has_relation(target, OBJ):
            actions = self.pathfind_to(target)
            heuristics['owned'] = get_heuristic(actions), actions

        # is there one nearby?
        if nodes_are_adjacent(self, target):
            actions = [('take',target)]
            heuristics['nearby'] = get_heuristic(actions), actions
        
        if self.SimulaeNode.has_relation(target, OBJ):

            relation = self.get_relation(target)

            target_location = relation.get_location()

            if target_location is None:
                # do we know where any might be? -> search
                actions = [('search',target)]
                heuristics['location'] = get_heuristic(actions), actions
            else: # do we know where any are? -> goto exact location
                actions = self.pathfind_to(target_location)
                actions.append(('acquire',target))
                heuristics['location'] = get_heuristic(actions), actions

        for route, (heuristic, actions) in heuristics.items():

            optimal_route = min(heuristics, key=heuristic)

            return heuristics[optimal_route][1] # actions



        # do we know how to make it?
        if self.can_make(target):

            crafting_loc, required_components = self.get_recipe(target)
            actions = []

            if crafting_loc and required_components:

                for component in required_components:
                    actions.append( self.acquire(component) )

                actions.append(self.pathfind_to(crafting_loc))

                actions.append(('make',target))

            else: # cannot make 'target'
                return actions

        # we are SOL
        return []

    def get_recipe(self, target):
        # todo AE : implement
        return (None, None)


    def Turn_RecursiveMinMax(self, ngin_state):
        pass

    def Turn_Random(self, ngin_state, actor):
        pass

    def Turn_StackMinMax(self, ngin_state):

        #           depth, turn num, state, moves
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

                if turn_state == 0: # actors turn
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
        return len([ node for node in state.relations[nodetype] if node.references['FAC'] == actor.id])

    def only_one(nt_per_actor):
        has_one = False
        for val in nt_per_actor:
            if val[1] != 0:
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
    
def get_heuristic(actions):
        # todo AE : implement
        return 0

def nodes_are_adjacent(node1, node2):

    loc1 = node1.SimulaeNode.get_reference(LOC)

    if loc1 and loc1.has_relation(node2):
        return True
    return False

    # todo ae : reimplement this

    loc2 = node2.get_reference(LOC)

    if loc1 == loc2:
        return True

    return False

def generate_individual(location=None):

        individual = generate_simulae_node(POI, "NODE")

        individual.nodetype = POI

        if location:
            individual.update_relation(location)
        
        return individual

def generate_food_item():
    food = generate_simulae_node(OBJ, "FOOD")

    food.set_check('edible', True)
    food.set_check('consumable', True)
    food.set_attribute('nutrition', 10)

    return food

def generate_drink_item():
    drink = generate_simulae_node(OBJ, "DRINK")

    drink.set_check('drinkable', True)
    drink.set_check('consumable', True)
    drink.set_attribute('hydration', 10)

    return drink


def NGIN_AI_test():

    actor = NGIN_Simulae_Actor(generate_individual())

    print('Actor:', actor.SimulaeNode.id)

    actor.SimulaeNode.set_attribute('hunger', 10)
    actor.SimulaeNode.set_attribute('thirst', 20)
    actor.SimulaeNode.set_attribute('exhaustion', 70)
    actor.SimulaeNode.set_attribute('socialize', 20)

    print('problem_solve:')

    actions = actor.problem_solve()

    print("problem_solve yielded: ",actions)

    #print('Action:', actor.Turn_StackMinMax(state) )


if __name__ == '__main__':
    print('NGIN_AI | Running tests')

    NGIN_AI_test()
