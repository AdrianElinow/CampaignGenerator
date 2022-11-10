

import sys,random
import json

import pprint

''' Mission Pattern:

entry format:
    type, label, interactions, state?

Evaluate Contexts
Generate Options    
    Intel
        Hostile
            + HVT
            + H Element
            + H Loc
            + H Source
        + NPC
        + OBJ
        + Neutral Party 
'''

class NGIN:

    def __init__(self, struct_filepath, madlib_filepath):

        self.struct =  json.load(open(struct_filepath))
        self.madlibs = json.load(open(madlib_filepath))
        
        self.pp = pprint.PrettyPrinter(indent=4)

        self.nodes = 0
        self.intel_opts = [
            [0,'TGT','HVT',"<HVT name>",0,[]],
            [0,'LOC','OFL',"<Opfor Loc>",0,[]],
            [0,'TGT','HVT',"<Opfor SRC>",0,[]],
            [0,'PTY','OFE',"<Opfor Elmt>",0,[]],
            [0,'TGT','NPC',"<NPC name>",0,[]],
            [0,'TGT','OBJ',"<OBJ name>",0,[]]
        ]
        self.history = []

        self.subtype_translation = {
            "HVT":"High-Value Target",
            "OBJ":"Objective",
            "OFE":"Opfor Element",
            "VIP":"VIP",
            "NPC":"Neutral Party",
            "ALY":"Ally",
            "NTL":"Neutral",
            "ALC":"Allied Location",
            "OFL":"Opfor Location"
        }

        ''' state entry format:
            id, type, subtype, label, interactions, state
        '''
        # starting state
        self.state = {
            "INV":{
                "OBJ":[],
                "HVT":[],
                "OFE":[]
            },
            "TGT":{
                "OBJ":[],
                "VIP":[],
                "HVT":[],
                "NPC":[]
            },
            "PTY":{
                "ALY":[],
                "OFE":[],
                "NTL":[]
            },
            "LOC":{
                "ALC":[],
                "OFL":[],
                "NTL":[]
            }
        }
        self.generate_init()


    def generate_spec(self, ntype, subtype, label="" ):

        self.nodes += 1

        return [self.nodes, ntype, subtype, random.choice(self.madlibs[ntype][subtype]), 0, [] ]

 
    def generate_intel( self ):

        chosen = random.choice(self.intel_opts)
        chosen[0] = self.nodes
        if self.madlibs[chosen[1]][chosen[2]]:
            chosen[3] = random.choice( self.madlibs[chosen[1]][chosen[2]] )
            self.madlibs[chosen[1]][chosen[2]].remove(chosen[3])
        self.nodes += 1

        return chosen

    def generate_init( self ):

        #[0,'TGT','HVT',"<HVT name>",0,[]]

        self.state["PTY"]["ALY"] = [ self.generate_spec("PTY","ALY") for i in range(2) ]
        self.state["LOC"]["ALC"] = [ self.generate_spec("LOC","ALC") for i in range(2) ]
        self.state["TGT"]["VIP"] = [ self.generate_spec("TGT","VIP") for i in range(1) ]

        self.state["TGT"]["HVT"] = [ self.generate_spec("TGT","HVT") for i in range(2) ]
        #self.state["TGT"]["HVT"] = [ self.generate_spec("TGT","HVT") for i in range(1) ]

    def generate_story( self ):

        # if state empty, roll intel
        #print( [ ngin_struct[t][st] for t in ngin_struct for st in ngin_struct[t] ] )
        
        opts = [ e for t in self.state for st in self.state[t] for e in self.state[t][st] ]
        
        if not opts:
            
            intel = self.generate_intel()
            opts = [ intel ]

        while opts:
            print('~'*25)

            # generate
            #print('opts')
            #opts = [ e for t in self.state for st in self.state[t] for e in self.state[t][st] ]

            if not opts:
                print('Gathering Intel...')
                intel = self.generate_intel()
                self.state[intel[1]][intel[2]].append(intel)
                
            opts = [ e for t in self.state for st in self.state[t] for e in self.state[t][st] ]
        
            for i in self.state['INV']:
                if self.state['INV'][i]:
                    print('INV:',i)
                    for entry in self.state['INV'][i]:
                        print('\t',self.subtype_translation[entry[2]],':',entry[3])
            print('Opts:')
            for o in opts:
                print('\t',self.subtype_translation[o[2]],':',o[3])


            node = random.choice( opts )
            opts.remove(node)


            mission = random.choice( self.struct[node[1]][node[2]] )
            

            '''
            while mission[0] in node[5]:
                mission = random.choice(self.struct[node[1]][node[2]])
            '''
            # Display mission
            print( mission[0], self.subtype_translation[node[2]],':', node[3] )

            node[4] += 1
            #node[5].append(mission[0])

            if len(mission) > 1:
                outcomes = mission[1:]
                

                for r in outcomes:
                    if r == '-':
                        if node in self.state[node[1]][node[2]]:
                            self.state[node[1]][node[2]].remove(node)
                    elif r == 'INT':
                        intel = self.generate_intel()
                        self.state[intel[1]][intel[2]].append(intel)
                        print("New Intel on",intel[2], intel[3])

                    elif r == 'ALY':

                        if mission[0] == 'Recruit':
                            intel = [node[0], 'PTY','ALY',node[3],node[4],node[5]]
                        else:
                            intel = [self.nodes, 'PTY','ALY','<ALY>',1,[]]
                        self.state[intel[1]][intel[2]].append(intel)
                        self.nodes += 1
                        print('New Ally',intel[2], intel[3])

                    elif r == 'OBJ':
                        print('fix',r)

                    elif r == 'ALC':
                        intel = [self.nodes, 'LOC','ALC','<ALC>',1,[]]
                        self.state[intel[1]][intel[2]].append(intel)
                        self.nodes += 1
                        print("New Allied Loc",intel[2], intel[3])

                    elif r == 'OFL':

                        self.state[node[1]][node[2]].remove(node)
                        node[2] = 'OFL'
                        self.state[node[1]][node[2]].append(node)


                    elif r == '%INT':
                        if random.randrange(0,6) == 6:
                            intel = self.generate_intel()
                            self.state[intel[1]][intel[2]].append(intel)
                            print('New Intel on',intel[2],intel[3])

                    elif r == '%ALY':

                        if random.randrange(0,6) == 6:
                            self.state[node[1]][node[2]].remove(node)

                            intel = [self.nodes, 'PTY','ALY','<ALY>',node[4],node[5]]
                            self.state[intel[1]][intel[2]].append(intel)
                            self.nodes += 1
                            print("New Ally",intel[3])

                    elif r == '%OBJ':
                        if random.randrange(0,6) == 6:
                            intel = [self.nodes, 'TGT','OBJ','<OBJ>',1,[]]
                            self.state[intel[1]][intel[2]].append(intel)
                            self.nodes += 1
                            print("New OBJ",intel[4])

                    elif r == 'INV':

                        self.state[node[1]][node[2]].remove(node)
                        self.state['INV'][node[2]].append(node)
                        print("Added")

                    else:
                        print('wtf does\'',r,'\'mean?')


            '''
            print('state:',end='\n')
            intel = [ (st,e) for t in self.state for st in self.state[t] for e in self.state[t][st]]
            for e in intel:
                print('\t',e)
            '''

            opts = [ e for t in self.state for st in self.state[t] for e in self.state[t][st] ]

            try:
                input()
            except KeyboardInterrupt:
                break

def main():
    
    ngin = NGIN( './story_gen_struct.json', './madlib_generic.json' )

    ''' history entry format
    (operation type, objective, mission, time)
    '''
    ngin.generate_story( )




if __name__ == '__main__':
    main()

    