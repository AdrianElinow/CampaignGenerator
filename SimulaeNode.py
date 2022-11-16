

import json, sys, random, os
from pprint import pprint


class SimulaeNode:

    def __init__(self, given_id, references={
                            "name":None,
                            "nodetype":"OBJ",
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
                        relationships={}, 
                        checks={}, 
                        abilities={}):
        self.id = given_id
        self.references = references
        self.attributes = attributes
        self.relationships = relationships if references['nodetype'] in ['POI','PTY'] else None
        self.checks = checks
        self.abilities = abilities


    def update_relationship( self, node, interaction=None, reciprocate=False, new_relationship=True ):
        
        policy_diff = self.policy_diff( node.references['Policy'] )

        #print(policy_diff)
        self.relationships[ node.id ] = {
            "nodetype":node.references['nodetype'],
            "Policy":policy_diff,
            "Reputation":[0,0],
            "Interractions":1,
            "Disposition":"Neutral"
        }

        if reciprocate:
            node.update_relationship( self, reciprocate=False )


    def has_relationship( self, node ):
        
        if self.relationships[node.id]:
            return True
        return False


    def policy_diff( self, compare_policy ):

        summary = {}
        diff = 0

        for factor, policy in self.references['Policy'].items():
            
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


def SimulaeNode_test():

    raw_nodes = json.load( open('./nodes_structure.json') )

    state = {
        "FAC":{},
        "POI":{},
        "PTY":{},
        "LOC":{},
        "OBJ":{}
    }

    for k,v in raw_nodes['POI'].items():

        state[ v['references']['nodetype'] ][ v['id'] ] = SimulaeNode(   v['id'], 
                                                    v['references'], 
                                                    v['attributes'],
                                                    v['relationships'],
                                                    v['checks'],
                                                    v['abilities'] )
    # introduce each other

    for poi_id_a, poi_node_a in state['POI'].items():
        for poi_id_b, poi_node_b in state['POI'].items():
            if poi_id_a == poi_id_b:
                continue

            poi_node_a.update_relationship( poi_node_b, reciprocate=True )

    for nid, node in state['POI'].items():
        pprint(node.__dict__)




if __name__ == '__main__':
    SimulaeNode_test()


