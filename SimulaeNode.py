

import json, sys, random, os
from enum import Enum

#from json import JSONEncoder
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

ALL_NODE_TYPES = ['FAC','POI','PTY','LOC','OBJ']
NODETYPES = ['POI','PTY','LOC','OBJ'] # person, people, place, thing
SOCIAL_NODE_TYPES = ['FAC','POI','PTY']
GROUP_NODE_TYPES = ['FAC','PTY']
PEOPLE_NODE_TYPES = ['POI','PTY']
INANIMATE_NODE_TYPES = ['LOC','OBJ']


class SimulaeNode:

    # id, ntype, refs, attrs, reltn, checks, abilities

    def __init(self):
        pass

    def __init__(self,  given_id=None, 
                        nodetype="OBJ",
                        references={
                            "name":None,
                            "FAC":None,
                            "policy":{
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
            elif node.nodetype in ['FAC','PTY'] and node.relations[self.nodetype][self.id]['Disposition'] == 'Member':
                return True

        elif self.nodetype == 'FAC':

            if node.nodetype in INANIMATE_NODE_TYPES and node.id in self.relations['PPT'][node.nodetype]:
                return True
            elif node.nodetype in PEOPLE_NODE_TYPES and self.relations[node.nodetype][node.id]['Disposition'] == "Member":
                return True

        return False


    def update_relationship( self, node, interaction=None, reciprocate=False, new_relationship=True ):
        
        if not node:
            raise TypeError
        if node.nodetype not in SOCIAL_NODE_TYPES:
            print(node.nodetype," not in ", SOCIAL_NODE_TYPES)
            raise ValueError

        policy_diff = self.policy_diff( node.references['policy'] )

        self.relations[node.nodetype][ node.id ] = {
            "nodetype":node.nodetype,
            "policy":policy_diff,
            "Reputation":[0,0],
            "Interractions":1,
            "Disposition":self.get_policy_disposition(policy_diff[0])
        }

        if reciprocate:
            node.update_relationship( self, reciprocate=False )


    def has_relationship( self, node ):
        
        if self.relations[node.ntype][node.id]:
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

        for factor, policy in self.references['policy'].items():
            
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


def generate_simulae_node(node_name, node_type=None):

    name = node_name

    nodetype = random.choice( NODETYPES ) if node_type == None else node_type
    
    _policies = ["Economy","Liberty","Culture","Diplomacy","Militancy","Diversity","Secularity","Justice","Natural-Balance","Government"]

    references={
        "name":name,
        "FAC":None,
        "policy":{}
    }

    for policy in _policies:
        references['policy'][policy] = random.choice(POLICIES[policy])

    attributes = {}
    relations  = { nt:{} for nt in ALL_NODE_TYPES }
    checks     = {}
    abilities  = {}

    # id, nodetype, refs, attrs, reltn, checks, abilities
    return SimulaeNode( name, nodetype, references, attributes, relations, checks, abilities )

def SimulaeNode_test():

    fac_red = generate_simulae_node('RED', 'FAC')
    fac_blu = generate_simulae_node('BLU', 'FAC')

    poi_node_a = generate_simulae_node('A', 'POI')
    poi_node_b = generate_simulae_node('B', 'POI')

    ##

    fac_red.update_relationship( fac_blu, reciprocate=True)
    poi_node_a.update_relationship( poi_node_b, reciprocate=True)
    fac_red.update_relationship(poi_node_a, reciprocate=True)
    fac_blu.update_relationship(poi_node_a, reciprocate=True)
    fac_red.update_relationship(poi_node_b, reciprocate=True)
    fac_blu.update_relationship(poi_node_b, reciprocate=True)

    ##
    
    pprint(fac_red.toJSON())
    pprint(fac_blu.toJSON())
    pprint(poi_node_a.toJSON())
    pprint(poi_node_b.toJSON())

    print('Done')

    '''
    with open('nodes_structure_sv.json','w') as sv:
        sv.write( json.dumps( state.toJSON() , indent=4) )
        print('written')
    '''


if __name__ == '__main__':
    SimulaeNode_test()


