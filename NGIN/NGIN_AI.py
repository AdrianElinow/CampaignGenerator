from enum import Enum

from .SimulaeNode import *

STATUS_THRESHOLDS = "status_thresholds"
THREAT = "threat"
HUNGER = "hunger"
THIRST = "thirst"
DRINK = "drink"
SLEEP = "sleep"
SICK = "sick"
TEMPERATURE = "temperature"
COLD = "cold"
HOT = "hot"
EXHAUSTION = "exhaustion"
LONELINESS = "loneliness"
LOW = "low"
HIGH = "high"
MINIMUM = "min"
MAXIMUM = "max"
VALUE = "value"

STATUS_ATTRIBUTES = [HUNGER, THIRST, HOT, COLD, EXHAUSTION, LONELINESS, SICK]

PRIORITY_MODIFIERS = "priority_modifiers"
CRITICAL_PRIORITY = "critical_priority"
HIGH_PRIORITY = "high_priority"
MEDIUM_PRIORITY = "medium_priority"
LOW_PRIORITY = "low_priority"

TASK_PRIORITIES = [CRITICAL_PRIORITY, HIGH_PRIORITY, MEDIUM_PRIORITY, LOW_PRIORITY]

class Action(Enum):
    GOTO = 1
    ACQUIRE = 2
    TAKE = 3
    USE = 4
    MAKE = 5
    SEARCH = 6
    INTERACT = 7

class TaskPlan():
    def __init__(self, target, action, pre_actions=None, post_actions=None):
        self.target = target
        self.action = action
        self.pre_actions = pre_actions
        self.post_actions = post_actions
        self.heuristic = -1

        h = get_heuristic(self, target, self.all_actions())
        self.heuristic = h

    def all_actions(self):
        all = []
        
        if self.pre_actions:
            all.extend(self.pre_actions)

        all.append(self.action)

        if self.post_actions:
            all.extend(self.post_actions)

        return all
    
    def next_action(self):
        
        if self.pre_actions:
            return self.pre_actions.pop(0)
        
        if self.action:
            action = self.action
            self.action = None
            return action

        if self.post_actions:
            return self.post_actions.pop(0)
        

    def summary(self):
        summary = str(self)
        summary += "\n\tActions: ["
        first = True
        for action in self.all_actions():
            summary += f'{'' if first else ', '}{str(action)}'
            first = False
        summary += "]"
        return summary

    def __str__(self):
        return f"Task : [{self.heuristic}] for [{len(self.all_actions())} actions on {self.target}]"

class NGIN_Simulae_Actor(SimulaeNode):

    def __init__(self, simulae_node):
        super().__init__(simulae_node)
        self.SimulaeNode: SimulaeNode = simulae_node

        self.inventory = {}

        self.priorities: list = []
        self.plans = {}

        self.tasks = { priority:[] for priority in TASK_PRIORITIES}

        self.Attributes[STATUS_THRESHOLDS] = {
            THREAT: {
                MINIMUM: 10,
                LOW: 20,
                VALUE: 0,
                HIGH: 80,
                MAXIMUM: 90
            },
            HUNGER: {
                MINIMUM: 10,
                LOW: 20,
                VALUE: 0,
                HIGH: 80,
                MAXIMUM: 90
            },
            THIRST: {
                MINIMUM: 10,
                LOW: 20,
                VALUE: 0,
                HIGH: 80,
                MAXIMUM: 90
            },
            EXHAUSTION: {
                MINIMUM: 10,
                LOW: 20,
                VALUE: 0,
                HIGH: 80,
                MAXIMUM: 90
            },
            SICK: {
                MINIMUM: 10,
                LOW: 20,
                VALUE: 0,
                HIGH: 80,
                MAXIMUM: 90
            },
            TEMPERATURE: {
                MINIMUM: 10,
                LOW: 20,
                VALUE: 50,
                HIGH: 80,
                MAXIMUM: 90
            },
            LONELINESS: {
                MINIMUM: 10,
                LOW: 20,
                VALUE: 0,
                HIGH: 80,
                MAXIMUM: 90
            }
        }

        self.priority_modifiers = {
            THREAT: 10,
            THIRST: 9,
            HUNGER: 8,
            SICK: 7,
            EXHAUSTION: 6,
            HOT: 5,
            COLD: 5,
            LONELINESS: 4,
            CRITICAL_PRIORITY: 10,
            HIGH_PRIORITY: 8,
            MEDIUM_PRIORITY: 7,
            LOW_PRIORITY: 6
        }

    def plan(self):
        logDebug('plan()')

        if not self.priorities:
            self.prioritize()
        
        plans = {}

        for goal in self.priorities:
            logDebug('Planning for goal:', goal)

            priority, task = goal

            plan = self.plan_task(task)

            if plan:
                plans[task] = plan
                continue
            
            logDebug('no plan for',task)
        
        self.plans = plans
        
    def plan_task(self, task: str) -> TaskPlan:
        logDebug('plan_task(',task,')')

        if task in STATUS_ATTRIBUTES:
            return self.plan_status_task(task)
        elif task is THREAT:
            return self.plan_threat_reaction()
        else:
            #print('no planning for',task)
            return task

    def plan_status_task(self, task):
        logDebug('plan_status_task(',task,')')

        if task in STATUS_ATTRIBUTES:
            
            # [HUNGER, THIRST, SLEEP, SICK, TEMPERATURE, HOT, COLD, EXHAUSTION, SOCIALIZE]

            if task == HUNGER:
                acquisition = self.acquire(SimulaeNode(given_id='food', nodetype=OBJ))
                return TaskPlan('food',Action.USE,acquisition)
            elif task == THIRST:
                acquisition = self.acquire(SimulaeNode(given_id='drink', nodetype=OBJ))
                return TaskPlan('drink',Action.USE,acquisition)
            elif task == SLEEP:
                acquisition = self.acquire(SimulaeNode(given_id='bed', nodetype=OBJ))
                return TaskPlan('bed',Action.USE,acquisition)
            elif task == SICK:
                acquisition = self.acquire(SimulaeNode(given_id='medicine', nodetype=OBJ))
                return TaskPlan('medicine',Action.USE,acquisition)
            elif task == LONELINESS:
                return TaskPlan('friend',Action.INTERACT,[Action.SEARCH])

        return self.acquire_vague_target(task)

    def plan_threat_reaction(self):
        logDebug('plan_threat_reaction()')

        return None

    def act_next(self, prioritized=False):
        logDebug('act_next(',prioritized,')')

        if not self.priorities:
            if prioritized:
                #print("no priorities??")
                return None

            #print('re-prioritizing')
            self.prioritize()
            return self.act_next(prioritized=True)

        task = self.priorities[0]

        if not task:
            #print('no task?')
            return None
        
        priority, goal = task

        if goal not in self.plans or self.plans[goal] == None:
            self.plans[goal] = self.plan_task(goal)

        plan = self.plans[goal]

        #print(f"Need to solve: {goal} (priority: {priority})")

        if not plan:
            #print(f'no plan for {goal}')
            pass

        else:
            #print(plan.summary())

            self.act(plan)

    def act(self, plan: TaskPlan):
        ''' TODO AE : flesh this out '''

        next_action = plan.next_action()

        if next_action == Action.GOTO:
            print(f'went to {plan.target}')
        elif next_action == Action.USE:
            ''' consume item '''
            if plan.target in self.SimulaeNode.Relations[CONTENTS]:
                del self.SimulaeNode.Relations[CONTENTS][plan.target]
                print(f'consumed {plan.target}')
            else:
                raise KeyError(f"Cannot use {plan.target} -> not in inventory")

        elif next_action == Action.TAKE:
            ''' add item to inv '''
            self.SimulaeNode.Relations[CONTENTS][plan.target.ID] = plan.target
            print(f'took {plan.target}')
            



    def prioritize(self):
        logDebug('prioritize()')
        ''' Prioritize actions based on current needs '''
        ''' Follow rough Maslow's hierarchy of needs '''

        self.priorities = []

        # individuals have priority modifiers (based on their personality traits)

        # if we are threatened -> prioritize defense

        if self.is_threatened():
            self.priorities.append((self.priority_modifiers[THREAT], THREAT))

        # if we are starving, dehydrated, exhausted, deathly ill, etc

        if self.is_starving():
            self.priorities.append((self.priority_modifiers[HUNGER], HUNGER))
        if self.is_dehydrated():
            self.priorities.append((self.priority_modifiers[THIRST], THIRST))
        if self.is_exhausted():
            self.priorities.append((self.priority_modifiers[EXHAUSTION], EXHAUSTION))
        if self.is_overheated():
            self.priorities.append((self.priority_modifiers[HOT], HOT))
        if self.is_freezing():
            self.priorities.append((self.priority_modifiers[COLD], COLD))
        if self.is_ill():
            self.priorities.append((self.priority_modifiers[SICK], SICK))
        if self.is_lonely():
            self.priorities.append((self.priority_modifiers[LONELINESS], LONELINESS))

        # Also handle tasks by priority level

        for task_priority, tasks in self.tasks.items():
            for task in tasks:
                self.priorities.append((self.priority_modifiers[task_priority], task))

        # sort by priorty, ascending?
        self.priorities.sort( key=lambda x: x[0], reverse=False)

    def is_threatened(self):
        return False # todo AE: implement
    
    def is_starving(self):
        hunger = self.get_attribute(HUNGER)
        hunger_threshold = self.get_status_threshold(HUNGER, HIGH)
        if hunger and hunger_threshold and hunger >= hunger_threshold:
            return True
        return False 
    
    def is_dehydrated(self):
        thirst = self.get_attribute(THIRST)
        thirst_threshold = self.get_status_threshold(THIRST, HIGH)
        if thirst and thirst_threshold and thirst >= thirst_threshold:
            return True
        return False
    
    def is_exhausted(self):
        exhaustion = self.get_attribute(EXHAUSTION)
        exhaustion_threshold = self.get_status_threshold(EXHAUSTION, HIGH)
        if exhaustion and exhaustion_threshold and exhaustion >= exhaustion_threshold:
            return True
        return False
    
    def is_hot(self):
        temp = self.get_attribute(TEMPERATURE)
        temp_threshold = self.get_status_threshold(TEMPERATURE, HIGH)
        if temp and temp_threshold and temp >= temp_threshold:
            return True
        return False
    
    def is_overheated(self):
        temp = self.get_attribute(TEMPERATURE)
        temp_threshold = self.get_status_threshold(TEMPERATURE, MAXIMUM)
        if temp and temp_threshold and temp >= temp_threshold:
            return True
        return False
    
    def is_cold(self):
        temp = self.get_attribute(TEMPERATURE)
        temp_threshold = self.get_status_threshold(TEMPERATURE, LOW)
        if temp and temp_threshold and temp <= temp_threshold:
            return True
        return False

    def is_freezing(self):
        temp = self.get_attribute(TEMPERATURE)
        temp_threshold = self.get_status_threshold(TEMPERATURE, MINIMUM)
        if temp and temp_threshold and temp <= temp_threshold:
            return True
        return False
    
    def is_ill(self):
        sick = self.get_attribute(SICK)
        sick_threshold = self.get_status_threshold(SICK, LOW)
        if sick and sick_threshold and sick >= sick_threshold:
            return True
        return False
    
    def is_lonely(self): 
        loneliness = self.get_attribute(LONELINESS)
        loneliness_threshold = self.get_status_threshold(LONELINESS, LOW)
        if loneliness and loneliness_threshold and loneliness >= loneliness_threshold:
            return True
        return False
    
    def pathfind_to(self, target):
        return [(Action.GOTO,target)]
    
    def can_make(self, target):
        return False # todo AE: implement
    
    def get_recipe(self, target):
        return 'workstation', ['component1','component2'] # todo AE: implement
    
    def get_status_threshold(self, threshold: str, subkey: str = None) -> int | float | None:
        logDebug("get_status_threshold(",threshold,", ",subkey,")")

        thresholds = self.get_attribute(STATUS_THRESHOLDS)

        if thresholds and threshold in thresholds:
            if subkey and subkey in thresholds[threshold]:
                return thresholds[threshold][subkey]
            elif not subkey:
                return thresholds[threshold]

        return None

    def has_vague(self, target):
        return False

    def acquire_vague_target(self, target):

        actions = []
        heuristics = {}

        if self.has_vague(target):
            return [] # base case -> already have it
        
        relations = self.SimulaeNode.get_relations_by_criteria(target)

        if relations: # do we know where any are?
            heuristics['owned'] = get_best_heuristic(relations, lambda x: self.pathfind_to(x)) # find optimal relation

        nearby = get_targets_nearby_node(self, target)
        if nearby:
            actions = [(Action.TAKE,target)]
            heuristics['nearby'] = get_heuristic(actions), actions

        optimum_heuristic = None
        optimum_option = None

        for option, (heuristic, actions) in heuristics:

            if optimum_option == None or heuristic < optimum_heuristic:
                optimum_option = option
                optimum_heuristic = heuristic

        if optimum_option:
            actions = heuristics[optimum_option][1]

            return TaskPlan(target, actions)

        return None
    
    def has_node(self, node: SimulaeNode):

        relation = self.get_relation(node)
        if relation:
            return True
        return False


    def acquire(self, target : SimulaeNode):
  
        # do we already have one?
        if self.has_node(target):
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
            actions = [(Action.TAKE,target)]
            heuristics['nearby'] = get_heuristic(actions), actions
        
        if self.SimulaeNode.has_relation(target, OBJ): # do we know where any are?

            relation = self.get_relation(target) 

            target_location = relation.get_location()

            if target_location is None:
                # do we know where any might be? -> search
                actions = [(Action.SEARCH,target)]
                heuristics['location'] = get_heuristic(actions), actions

            else: # do we know where any are? -> goto exact location
                actions = self.pathfind_to(target_location)
                actions.append((Action.ACQUIRE,target))
                heuristics['location'] = get_heuristic(actions), actions

        for route, (heuristic, actions) in heuristics.items():

            optimal_route = min(heuristics, key=heuristic) # find optimal route

            return heuristics[optimal_route][1] # actions



        # do we know how to make it?
        if self.can_make(target):

            crafting_loc, required_components = self.get_recipe(target)
            actions = []

            if crafting_loc and required_components: # can make item with workstation

                for component in required_components: # acquire components
                    actions.append( self.acquire(component) )

                actions.append(self.pathfind_to(crafting_loc)) # go to workstation

                actions.append((Action.MAKE,target)) # make item

            elif required_components: # can make item without workstation

                for component in required_components:
                    actions.append( self.acquire(component) ) # acquire components
                
                actions.append((Action.MAKE,target)) # make item

            else: # cannot make 'target'
                return actions

        # we are SOL
        return []
    
    def status_summary(self):
        summary = f"Actor: {self.SimulaeNode.summary()}\n"
        
        for attr in self.SimulaeNode.attributes:
            summary += f"{attr}: {self.get_attribute(attr)}\n"

        return summary
    

def get_targets_nearby_node(node, target_criteria):
    
    loc = node.SimulaeNode.get_location()
    if loc:
        return loc.get_relations_by_criteria(target_criteria)
    return []


def get_best_heuristic(dataset, action, minimize=True):
    
    optimum_output = None
    best = None

    for item in dataset:
        output = get_heuristic(action(item))

        if not optimum_output:
            optimum_output = output
            best = item
        elif minimize and output < optimum_output:
            optimum_output = output
            best = item
        elif not minimize and output > optimum_output:
            optimum_output = output
            best = item
    
    return best

def get_heuristic(actor, target, actions):
    value = 0

    for action in actions:
        if not action:
            continue
        
        act = action
        if act == Action.GOTO:
            print('getting distance from ',actor,'to',target)
            #value += distance_between(actor, target)
            value += 1
        elif act == Action.TAKE:
            value += 1
        elif act == Action.USE:
            value += 1
        elif act == Action.MAKE:
            value += 2
        else:
            value += 3

    return value


def distance_between(actor, target):
    if nodes_are_adjacent(actor, target):
        return 1
    else:
        return 2 # todo AE: implement

def nodes_are_adjacent(node1, node2):

    containing_loc = node1.SimulaeNode.get_reference(LOC)

    if containing_loc and containing_loc.has_relation(node2):
        return True
    return False



def generate_individual(location=None):

        individual = SimulaeNode(nodetype=POI)

        individual.set_reference(NAME, "individual")

        individual.set_attribute(HUNGER, 0)
        individual.set_attribute(THIRST, 0)
        individual.set_attribute(EXHAUSTION, 0)
        individual.set_attribute(SICK, 0)
        individual.set_attribute(TEMPERATURE, 0)
        individual.set_attribute(LONELINESS, 0)
        individual.set_attribute(EXHAUSTION, 0)

        if location:
            individual.update_relation(location)
        
        return individual

def generate_food_item():
    food = SimulaeNode(nodetype=OBJ)

    food.set_reference(NAME, "food")

    food.set_check('edible', True)
    food.set_check('consumable', True)
    food.set_attribute('nutrition', 10)

    return food

def generate_drink_item():
    drink = SimulaeNode(nodetype=OBJ)

    drink.set_reference(NAME, "drink")

    drink.set_check('drinkable', True)
    drink.set_check('consumable', True)
    drink.set_attribute('hydration', 10)

    return drink
