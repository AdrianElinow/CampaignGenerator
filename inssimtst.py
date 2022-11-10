



def main():

    factions = {
        "Insurgents":{
            #"TRP":[(10,'R','X'),(5,'M','X')],
            "OPP":["Security"],
            'ADJ':[],
            "LOC":{'R':[(10,'R','X')],'Q':[],'M':[(5,'M','X')]},
            "OBJ":[],
            "HVT":[]
        },
        "Security":{
            #"TRP":[(10,'D','X'),(5,'C','X')],
            "OPP":["Insurgents"],
            'ADJ':[],
            "LOC":{'F':[],'D':[(10,'D','X')],'C':[(5,'C','X')]},
            "OBJ":[],
            "HVT":[]
        }
    }
    
    worldmap = {'A':['B','J','K'],
                'B':['A','C','J'],
                'C':['B','D','E','H','I'],
                'D':['C','E','G','F'],
                'E':['C','D','G'],
                'F':['D','G','H'],
                'G':['D','E','F'],
                'H':['F','C'],
                'I':['C','J'],
                'J':['A','B','I'],
                'K':['A','L','N','O'],
                'L':['K'],
                'M':['N','P'],
                'N':['K','M','O','Q'],
                'O':['K','N'],
                'P':['M','Q'],
                'Q':['N','P','R'],
                'R':['Q']
                }

    actions = ['occupy','defend','recruit']


    while True:

        if not (factions['Insurgents']['LOC'] and factions['Insurgents']['LOC']) and \
            (factions['Security']['LOC'] and factions['Security']['LOC']):
            break
        #display
        print(factions["Insurgents"])
        print(factions["Security"])

        for f,d in factions.items():

            print(f,'turn')

            #territory scan
            for loc in d['LOC']:
                for adj in worldmap[loc]:
                    if adj not in d['ADJ']:
                        d['ADJ'].append(adj)

            i = len(d['TRP'])
            for j in range(i):

                s,l,m = d['TRP'].pop()

                if s == 0:
                    continue
                elif s == 1:
                    d['TRP'].append( (s,l,'R') )
                else:
                    tadj = [ p for p in worldmap[l] if p in d['ADJ'] ]

                    if m == 'X':
                        for p in tadj:
                            # check enemy?
                            if p in factions[d['OPP'][0]]['LOC']:
                                # battle

                                opfor = [ (os,ol,om) for os,ol,om in factions[d['OPP'][0]]['TRP'] if ol == p ]
                                os,ol,om = 0,0,0
                                o_str = 0
                                # calc opp strength
                                if len(opfor) > 1:
                                    for ss,sl,sm in opfor:
                                        o_str += ss + (1 if om == 'D' else 0)
                                else:
                                    o_str = os

                                a_str = s

                                if (a_str > o_str) or ((s-os)-1) < 1:
                                    print('\trecruiting at ',l)
                                    # recruit
                                    d['TRP'].append(s-os,l,'R')
                                else:
                                    # occupy
                                    print('\tOccupied',p,'!')
                                    d['TRP'].append((((s-os)-1),p,'X'))
                                    d['TRP'].append((1,l,'H'))

                            else: # occupy
                                print('\tOccupied',p,'!')
                                d['TRP'].append((s-1,p,'X'))
                                d['TRP'].append((1,l,'H'))
                    elif m == 'D': #defend
                        for p in tadj:
                            # enemy nearby?
                            if tadj in factions[d['OPP']]['LOC']:
                                print('\tDefending at',l)
                                # hold
                                d['TRP'].append(s,l,'D')
                                continue
                        # recruit
                        print('\tRecruiting at',l)
                        d['TRP'].append(s,l,'R')

                    elif m == 'H':
                        print('\tRecruiting at',l)
                        d['TRP'].append(s,l,'R')
                    elif m == 'R':
                        print('\tRecruited +2 at ',l,'!')
                        d['TRP'].append(s+2,l,'X')

            for f,d in factions.items():
                print(f,'\n\ttroops:',d['TRP'],'\n\tlocs',d['LOC'],'\n\tfrontier:',d['ADJ'])

            input()



if __name__ == '__main__':
    main()







