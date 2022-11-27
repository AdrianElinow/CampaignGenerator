

import json, sys, random, os

#from json import JSONEncoder
from pprint import pprint


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
        self.references = references
        self.nodetype = nodetype
        self.attributes = attributes
        self.relations = relations
        self.checks = checks
        self.abilities = abilities

    def summary(self):
        return "{0}".format(self.references['name'])


    def check_membership(self, node):
        ''' check_membership(..., node) checks for relations between self and given node
                if node is of types OBJ or LOC, checks of self has ownership of node
                if node is of types FAC or PTY, checks that node has membership with self
        '''

        if not (node and node.nodetype and node.id):
            raise ValueError

        if self.nodetype in ['PTY','POI']:

            # check self's ownership of node
            if node.nodetype in ['OBJ','LOC'] and node.id in self.relations['PPT'][node.nodetype]:
                return True
            # check self's membership as apart of node
            elif node.nodetype in ['FAC','PTY'] and node.relations[self.nodetype][self.id]['Disposition'] == 'Member':
                return True

        elif self.nodetype in ['Fac']:

            if node.nodetype in ['OBJ','LOC'] and node.id in self.relations['PPT'][node.nodetype]:
                return True
            elif node.nodetype in ['PTY','POI'] and self.relations[node.nodetype][node.id]['Disposition'] == "Member":
                return True

        return False


    def update_relationship( self, node, interaction=None, reciprocate=False, new_relationship=True ):
        
        if not node:
            raise TypeError
        if node.nodetype not in ['FAC','POI','PTY']:
            raise ValueError

        policy_diff = self.policy_diff( node.references['policy'] )

        self.relations[node.nodetype][ node.id ] = {
            "nodetype":node.nodetype,
            "policy":policy_diff,
            "Reputation":[0,0],
            "Interractions":1,
            "Disposition":"Neutral"
        }

        if reciprocate:
            node.update_relationship( self, reciprocate=False )


    def has_relationship( self, node ):
        
        if self.relations[node.ntype][node.id]:
            return True
        return False


    def policy_diff( self, compare_policy ):

        summary = {}
        diff = 0

        for factor, policy in self.references['policy'].items():
            
            delta = abs( self.get_policy_index(factor, policy) - self.get_policy_index( factor, compare_policy[factor] ) )

            summary[factor] = [ "Agreement", "Civil", "Contentious",  "Opposition", "Diametrically Opposed" ][delta]
            diff += delta

        return diff, summary


    def get_policy_index(self, factor, policy):

        policies = {
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

        return policies[factor].index(policy[0])


    def toJSON(self):
        d = self.__dict__

        for k,v in self.relations.items():
            v =  v = { nid:node.__dict__ for nid, node in v.items() }
            d['relations'][k] = v

        return d



def jsonify( state ):

    d = state.__dict__

    for k,v in state.relations.items():

        v =  v = { nid:node.__dict__ for nid, node in v.items() }
        d['relations'][k] = v

    return d



def SimulaeNode_test():

    raw_nodes = json.load( open('./nodes_structure.json') )

    state = SimulaeNode(
            "state",
            "",
            {},
            {},
            {
                "FAC":{},
                "PTY":{},
                "POI":{},
                "OBJ":{},
                "LOC":{}
            },
            {},
            {}
        )


    '''
    {
        "FAC":{},
        "POI":{},
        "PTY":{},
        "LOC":{},
        "OBJ":{}
    }#'''

    for nodetype in state.relations.keys():

        print('Processing',nodetype,'\'s')

        for k,v in raw_nodes[nodetype].items():
            state.relations[ nodetype ][ v['id'] ] = SimulaeNode(   
                                                        v['id'], 
                                                        v['nodetype'],
                                                        v['references'], 
                                                        v['attributes'],
                                                        v['relations'],
                                                        v['checks'],
                                                        v['abilities'] )


    # introduce each other
    for poi_id_a, poi_node_a in state.relations['POI'].items():
        for poi_id_b, poi_node_b in state.relations['POI'].items():
            if poi_id_a == poi_id_b:
                continue

            poi_node_a.update_relationship( poi_node_b, reciprocate=True )

        for fac_id, fac_node in state.relations['FAC'].items():
            poi_node_a.update_relationship( fac_node, reciprocate=True )


    """
    for nid, node in state.relations['POI'].items():
        pprint(node.__dict__)
    #"""
    input("factions >")

    for fid, fnode in state.relations['FAC'].items():
        pprint(fnode.__dict__)
        for poi_id, poi_node in state.relations['POI'].items():
            print(poi_id,'membership in',fid, ':',fnode.check_membership(poi_node))
    
    print('Done')


    with open('nodes_structure_sv.json','w') as sv:
        sv.write( json.dumps( state.toJSON() , indent=4) )
        print('written')


if __name__ == '__main__':
    SimulaeNode_test()


