

import json, sys, random, os
from math import e
from enum import Enum

#from json import JSONEncoder
from ngin_utils import *
from pprint import pprint

POLICIES = {
    "Economy":      
        ["Communist", "Socialist", "Indifferent", "Capitalist", "Free-Capitalist"],
    "Liberty":      
        ["Authoritarian", "Statist", "Indifferent", "Libertarian", "Anarchist"],
    "Culture":      
        ["Traditionalist", "Conservative", "Indifferent", "Progressive", "Accelerationist"],
    "Diplomacy":    
        ["Globalist", "Diplomatic", "Indifferent", "Patriotic", "Nationalist"],
    "Militancy":    
        ["Militarist", "Strategic", "Indifferent", "Diplomatic", "Pacifist"],
    "Diversity":  
        ["Homogenous", "Preservationist", "Indifferent", "Heterogeneous", "Multiculturalist"],
    "Secularity":   
        ["Apostate", "Secularist", "Indifferent", "Religious", "Devout"],
    "Justice":      
        ["Retributionist", "Punitive", "Indifferent", "Correctivist", "Rehabilitative"],
    "Natural-Balance":  
        ["Ecologist", "Naturalist", "Indifferent", "Productivist", "Industrialist"],
    "Government":   
        ["Democratic", "Republican", "Indifferent", "Oligarchic", "Monarchist"]
}

FAC = 'FAC'
POI = 'POI'
PTY = 'PTY'
LOC = 'LOC'
OBJ = 'OBJ'

POLICY = "policy"
ADJACENT = "adjacent"

ALL_NODE_TYPES = [FAC,POI,PTY,LOC,OBJ]
NODETYPES = [POI,PTY,LOC,OBJ] # person, people, place, thing
SOCIAL_NODE_TYPES = [FAC,POI,PTY]
GROUP_NODE_TYPES = [FAC,PTY]
PEOPLE_NODE_TYPES = [POI,PTY]
INANIMATE_NODE_TYPES = [LOC,OBJ]


class SimulaeNode:

    # id, ntype, refs, attrs, reltn, checks, abilities

    def __init__(self,  given_id=None, 
                        nodetype=OBJ,
                        references={
                            "name":None,
                            FAC:None,
                            POLICY:{
                                "Economy":          ["Indifferent", 0.5],
                                "Liberty":          ["Indifferent", 0.5],
                                "Culture":          ["Indifferent", 0.5],
                                "Diplomacy":        ["Indifferent", 0.5],
                                "Militancy":        ["Indifferent", 0.5],
                                "Diversity":        ["Indifferent", 0.5],
                                "Secularity":       ["Indifferent", 0.5],
                                "Justice":          ["Indifferent", 0.5],
                                "Natural-Balance":  ["Indifferent", 0.5],
                                "Government":       ["Indifferent", 0.5]
                            }
                        }, 
                        attributes={
                            "interactions":0
                        }, 
                        relations={}, 
                        checks={}, 
                        abilities={}):

        self.id = given_id
        self.status = Status.ALIVE
        self.references = references
        self.nodetype = nodetype
        self.attributes = attributes
        self.relations = relations
        self.checks = checks
        self.abilities = abilities

    def summary(self):
        return "{0}".format(self.references['name'])

    def __str__(self):
        return self.summary()


    def check_membership(self, node):
        ''' check_membership(..., node) checks for relations between self and given node
                if node is of types OBJ or LOC, checks of self has ownership of node
                if node is of types FAC or PTY, checks that node has membership with self
        '''

        if not (node and node.nodetype and node.id):
            raise ValueError

        if self.nodetype in PEOPLE_NODE_TYPES:

            # check self's ownership of node
            if node.nodetype in INANIMATE_NODE_TYPES and node.id in self.relations['PPT'][node.nodetype]:
                return True
            # check self's membership as apart of node
            elif node.nodetype in GROUP_NODE_TYPES and node.relations[self.nodetype][self.id]['Disposition'] == 'Member':
                return True

        elif self.nodetype == FAC:

            if node.nodetype in INANIMATE_NODE_TYPES and node.id in self.relations['PPT'][node.nodetype]:
                return True
            elif node.nodetype in PEOPLE_NODE_TYPES and self.relations[node.nodetype][node.id]['Disposition'] == "Member":
                return True

        return False

    def get_adjacent_locations(self):
        
        if ADJACENT in self.references:

            adjacents = self.references[ADJACENT]

            if type(adjacents) == type(""):
                return [adjacents]

            return adjacents
        else:
            return []

    def add_adjacent_location(self, loc, reciprocate=True):
        
        self.add_reference(ADJACENT, loc.id)
        loc.add_reference(ADJACENT, self.id, reciprocate=False)

    def get_reference(self, key: str):
        
        if key in self.references:
            return self.references[key]

        return None

    def add_reference(self, key: str, value: str):
        
        if key in self.references:
            
            reference = self.references[key]

            if type(reference) == type(""):
                if reference is not value:
                    self.references[key] = [reference, value]
                    
            elif type(reference) == type([]):
                if value not in reference:
                    self.references[key].append(value)

        else:
            self.references[key] = value

    def get_attribute(self, key: str):
        
        if key in self.attributes:
            return self.attributes[key]

        return None


    def update_relation(self, node, interaction=None):
        
        if not node:
            raise ValueError
        
        if node.nodetype in self.relations:
            self.relations[node.nodetype] = {}

        if node.id not in self.relations[node.nodetype]:

            if node.nodetype in SOCIAL_NODE_TYPES:

                # social relationship
                if self.nodetype in SOCIAL_NODE_TYPES:
                    policy_diff = self.policy_diff( node.references['policy'] )

                    self.relations[node.nodetype][ node.id ] = {
                        "nodetype":node.nodetype,
                        "status":"new",
                        POLICY:policy_diff,
                        "Reputation":[0,0],
                        "Interractions":1,
                        "Disposition":self.get_policy_disposition(policy_diff[0])
                    }

                elif self.nodetype in INANIMATE_NODE_TYPES:
                    self.relations[node.nodetype][node.id] = "occupant"

            elif node.nodetype in INANIMATE_NODE_TYPES:
                self.relations[node.nodetype][node.id] = ADJACENT
        
            else:
                debug('Unhandled nodetype: ',node.nodetype)

        elif node.nodetype in SOCIAL_NODE_TYPES and self.nodetype in SOCIAL_NODE_TYPES:

            existing_relation = self.relations[node.id]
            
            policy_diff = self.policy_diff( node.references[POLICY] )
            
            existing_relation[POLICY] = node.policy
            existing_relation["Disposition"] = self.get_policy_disposition(policy_diff[0])
            
            if interaction != None:
                existing_relation['Reputation'][interaction[0]] += interaction[1]

            existing_relation["Interactions"] += 1

            # update w changes
            self.relations[node.id] = existing_relation
            
        else:
            debug("Unhandled relation")


    def has_relationship( self, node ):
        
        if self.relations[node.nodetype][node.id]:
            return True
        return False

    def get_policy_disposition(self, policy_diff_value):

        if policy_diff_value < 0:
            raise ValueError
        elif policy_diff_value == 0:
            return "Perfectly Aligned"
        elif policy_diff_value < 5:
            return "Aligned"
        elif policy_diff_value < 10:
            return "Neutral"
        elif policy_diff_value < 15:
            return "Opposed"
        elif policy_diff_value < 20:
            return "Strongly Opposed"
        elif policy_diff_value > 20:
            return "Diametrically Opposed"

    def policy_diff( self, compare_policy ):

        summary = {}
        diff = 0

        for factor, policy in self.references[POLICY].items():
            
            delta = abs( self.get_policy_index(factor, policy) - self.get_policy_index( factor, compare_policy[factor] ) )

            summary[factor] = [ "Agreement", "Civil", "Contentious",  "Opposition", "Diametrically Opposed" ][delta]
            diff += delta

        return diff, summary

    def get_policy_index(self, factor, policy):
        return POLICIES[factor].index(policy)


    def toJSON(self):
        d = self.__dict__

        for k,v in self.relations.items():
            v =  v = { nid:node for nid, node in v.items() }
            d['relations'][k] = v

        return d

class Status(Enum):
    ''' Simulae Node status '''
    ALIVE = 0
    DEAD = 1


def jsonify( state ):

    d = state.__dict__

    for k,v in state.relations.items():

        v =  v = { nid:node.__dict__ for nid, node in v.items() }
        d['relations'][k] = v

    return d


def generate_simulae_node(node_name, node_type, faction=None):

    name = node_name

    nodetype = random.choice( NODETYPES ) if node_type == None else node_type
    
    _policies = ["Economy","Liberty","Culture","Diplomacy","Militancy","Diversity","Secularity","Justice","Natural-Balance","Government"]

    references={
        "name":name,
        FAC:None,
        POLICY:{}
    }
    
    attributes = {}
    relations  = { nt:{} for nt in ALL_NODE_TYPES }
    checks     = {}
    abilities  = {}

    # Set Faction association
    if faction:
        references[FAC] = faction.id

    if nodetype in SOCIAL_NODE_TYPES:
        # Random Policy values
        for policy in _policies:
            references[POLICY][policy] = random.choice(POLICIES[policy])

    if nodetype in INANIMATE_NODE_TYPES:
        
        if nodetype == LOC:
           attributes['max_adjacent_locations'] = random.randrange(1,MAX_ADJACENT_LOCATIONS)

    # id, nodetype, refs, attrs, reltn, checks, abilities
    return SimulaeNode( name, nodetype, references, attributes, relations, checks, abilities )

def SimulaeNode_test():

    state = SimulaeNode("state","",{},{},{
                            FAC:{},
                            PTY:{},
                            POI:{},
                            OBJ:{},
                            LOC:{}
                        },{},{})

    fac_red = generate_simulae_node('RED', FAC)
    fac_blu = generate_simulae_node('BLU', FAC)

    poi_node_a = generate_simulae_node('A', POI, fac_red)
    poi_node_b = generate_simulae_node('B', POI, fac_blu)
    poi_node_c = generate_simulae_node('C', POI,)

    ##

    fac_red.update_relationship( fac_blu, reciprocate=True)
    poi_node_a.update_relationship( poi_node_b, reciprocate=True)
    fac_red.update_relationship(poi_node_a, reciprocate=True)
    fac_blu.update_relationship(poi_node_a, reciprocate=True)
    fac_red.update_relationship(poi_node_b, reciprocate=True)
    fac_blu.update_relationship(poi_node_b, reciprocate=True)

    ##

    state.add_node(fac_red)
    state.add_node(fac_blu)
    state.add_node(poi_node_a)
    state.add_node(poi_node_b)
    state.add_node(poi_node_c)
    
    pprint(fac_red.toJSON())
    pprint(fac_blu.toJSON())
    pprint(poi_node_a.toJSON())
    pprint(poi_node_b.toJSON())
    pprint(poi_node_c.toJSON())

    print('Done')

    return state

    '''
    with open('nodes_structure_sv.json','w') as sv:
        sv.write( json.dumps( state.toJSON() , indent=4) )
        print('written')
    '''


if __name__ == '__main__':
    SimulaeNode_test()


