
import sys,random
import json

def main():
    contextual_gen()



def contextual_gen():

    '''
    contexts = {
        "HLC":[],
        "NLC":[],
        "FLC":[],
        "OBJ":[],
        "VIP":[],
        "HVT":[],
        "ALY":[],
        "TGT":[],
        "EVT":[],
        "UNQ":["",""]
    }
    '''

    contexts = json.load( open('./contextual_inssim_contexts.json') )
    contextual_missions = json.load( open('./contextual_inssim.json') )

    times = ['{Day}','{Night}']

    print(contexts)

    while True:

        t = random.choice(times)
        optype = random.choice( list(contextual_missions.keys()) )
        objective = random.choice( list(contextual_missions[optype].keys()) )
        mission = random.choice( contextual_missions[optype][objective] )


        context_obj = ""
        # if contexts:
        if len(contexts[objective]) > 1 and objective != "UNQ":

            # add context
            if random.randrange(0,10) == 1:
                ctx = input( ("new "+objective+"> ") )
                if ctx:
                    contexts[objective].append(ctx)
                    context_obj = ctx
            else:
                #use random
                context_obj = random.choice( contexts[objective] )

        if not context_obj:
            context_obj = random.choice(contexts[objective])



        print( '[',optype,']', mission[0], context_obj, t)
        print(mission[1])



        if mission[1]:
            if mission[1] == '-':
                contexts[objective].remove(context_obj)
                print('removed',context_obj,'->',contexts[objective],end='')

            elif mission[1] == 'NLC':
                contexts[objective].remove(context_obj)
                contexts['NLC'].append('neutralized '+context_obj)
                print(contexts['NLC'],end='')

            elif mission[1] == 'INV':
                contexts[objective].remove(context_obj)
                contexts['INV'].append(context_obj)
                print(contexts[objective],'->',contexts["INV"],end='')

            elif mission[1] == '-INV':
                if context_obj in contexts['INV']:
                    contexts['INV'].remove(context_obj)
                print(contexts['INV'],end='')

            elif mission[1] == '+FLC':
                contexts[objective].remove(context_obj)
                contexts['FLC'].append(context_obj)
                print(contexts[objective],'->',contexts["FLC"])

            elif mission[1] == 'ALY':
                pass

            else:
                print('add',mission[1],'function',end='')



        try:
            input()
        except KeyboardInterrupt:
            break


def generic_gen():


    tmissions = {

        '[Direct Action]':[
            'Raid Location',
            'Recon Location',
            'Hostage Rescue',
            'Quick Reaction Force',
            'Riot Control',
            'Capture Target',
            'Eliminate HVT',
            'Support Allies',
            'Secure Target',
            'Intercept Target',
            'Interdict Convoy',
            'Defend Location',
            'Capture Target',
            'Destroy Target',
            'Extract Target'
        ],
        '[ Passive Ops ]':[
            'Recon Location',
            'Executive Protection VIP',
            'Investigate Location',
            'Gather Intel',
            'Exchange Objective',
            'Construct Defenses',
            'Stash Package',
            'Secure Resources',
            'Search Location',
            'Recruit Local Forces',
            'Advise Allies',
            'Escort Convoy',
            'Escort VIP',
            'Deliver Package',
            'Patrol Location'
        ],
        '[ Covert Ops  ]':[
            'Assassinate HVT',
            'Interrogate HVT',
            'Track HVT',
            'Escort VIP',
            'Evade Opfor',
            'Surveil Target',
            'Executive Protection',
            'Gather Intel',
            'Investigate Event',
            'Infiltrate Target',
            'Abduct HVT',
            'Decieve Target',
            'Recruit Source',
            'Train Local Forces'
        ]
    }

    times = ['{Day}','{Night}']


    while True:

        t = random.choice(times)
        op = random.choice( list(tmissions.keys()) )
        mission = random.choice( tmissions[op] )

        print( op, mission, t)

        try:
            input()
        except KeyboardInterrupt:
            break



if __name__ == '__main__':
    main()






