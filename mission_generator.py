
import json, sys, random, os
from pprint import pprint


class NGIN:

    def __init__(self, mission_struct, madlibs ):
        self.mission_struct = mission_struct
        self.madlibs = madlibs
        self.state = []
        self.state = self.generate_state(4) # generate start state with 4 initial nodes


    def generate_element( self ):
        ''' creates a new node with random attributes ''' 

        name = random.choice( [ m for m in self.madlibs \
            if m not in [ n for n,d,t,i in ( self.state ) ]] )
        return (name, \
                random.choice(['Friendly','Hostile','Neutral']), \
                random.choice(['POI',"PTY","LOC","OBJ"]), \
                0)


    def generate_state( self, num_elements ):
        ''' generates multiple new random nodes to (re)populate the game-state '''

        n_state = []
        for i in range(num_elements):
            n_state.append(self.generate_element())
        return n_state


    def generate_mission( self ):
        ''' selects (at random) a node in the game-state and randomizes a
                mission based on the available options for the chosen node's
                type and player-disposition
        '''

        subj = random.choice(self.state)
        name, disp, objective, interractions = subj

        # update subject (increment interaction stat)
        self.state[self.state.index(subj)] = name, disp, objective, interractions+1
        return subj, random.choice(self.mission_struct[disp][objective]),self.state


    def search(self, subject):
        ''' returns index of subject (by name and node-type only) 
                necessitated by the inefficient search structure's node organization
        '''

        index = False
        name, disp, obj, intr = subject

        for idx, elmt in enumerate(self.state):
            n,d,o,i = elmt
            if n == name and o == obj:
                index = idx

        return index


    def choose_mission(self):
        ''' To add more interractivity and user-control
                this function will give several available options to allow
                the player to 'control' their actions and interract
                with other nodes in a manner of their choice.
        '''
        pass


    def start(self):

        ''' Iterates through the game state generating missions based on
                available nodes in the state.
        '''

        while True:

            os.system('clear') # clear screen
            pprint(self.state)

            if not self.state:
                self.state = self.generate_state(1)


            subject, mission, self.state = self.generate_mission()

            #subject, mission, self.state = self.choose_mission()

            print(  '\n(',mission[1],') [',
                    mission[0],subject[0],'] {',
                    str(subject[1:]),'}')

            success = input('Success? (y/n) >')
            if success in ['y','yes']:

                if mission[0] in ['Eliminate','Destroy']:
                    # find and remove subject
                    subject_index = self.search(subject)
                    if subject_index:
                        del self.state[subject_index]
                    print('- removed',subject)

                elif mission[0] in ['Capture']:
                    n,d,o,i = subject

                    if o in ['LOC','OBJ']:
                        # find and modify subject
                        subject = n,"Friendly",o,i

                        # find and modify subject in game-state
                        subject_index = self.search(subject)
                        if subject_index:
                            self.state[subject_index] = subject
                        print('- changed',subject)

                    else:
                        # find and remove subject
                        subject_index = self.search(subject)
                        if subject_index:
                            del self.state[subject_index]
                        print('- removed',subject)


            if random.random() <= 0.5:
                # generate new element to keep sim going
                print('\nNew Intel')
                intel = self.generate_state( 1 )
                pprint(intel)
                self.state += intel

            if random.random() <= 0.4:
                # generate random event to keep things interesting
                subject, mission, self.state = self.generate_event()

                if mission:
                    print(  '\n(',mission[1],') [',
                            mission[0],subject[0],'] {',
                            str(subject[1:]),'}')

                    if mission[0] in ['Eliminate','Destroy']:
                        # find and remove subject in game-state
                        subject_index = self.search(subject)
                        if subject_index:
                            del self.state[subject_index]
                        print('- removed',subject)

            cmd = input('> ')
            if cmd in ['q','quit']:
                sys.exit(0)


    def generate_event( self ):
        
        # choose node as event basis
        subj = random.choice(self.state)
        name, disp, objective, interractions = subj

        # avoid modifying hostile nodes to maintain tension
        if disp in ['Neutral','Friendly']:
            roll = int(random.random() * 100)

            if roll < 25:
                print(name,'has', \
                    ('been captured by opfor' if objective in ['LOC','OBJ'] \
                    else "defected to the opfor"))

                # find and modify subject in game-state
                subj = name, "Hostile", objective, interractions+1
                subject_index = self.search(subj)
                if subject_index:
                    self.state[subject_index] = subj

            elif roll < 50:
                print(name, 'has been', \
                    ('Destroyed' if objective in ['LOC','OBJ'] \
                    else 'Killed'))

                # find and remove subject in game-state
                subject_index = self.search(subj)
                if subject_index:
                    del self.state[subject_index]
                print('- removed',subj)
            
            # no mission for these types of random events
            return subj, None, self.state

        # 
        return  subj, \
                random.choice(self.mission_struct[disp][objective]), \
                self.state


def main():
    
    ''' required import(s) '''
    mission_struct = json.load( open( sys.argv[1] ) )
    madlibs = [
        "Alpha",
        "Beta",
        "Delta",
        "Zeta",
        "Omicron",
        "Omega",
        "Lambda",
        "Tau",
        "Gamma",
        "Sigma",
        "Eagle",
        "Wolf",
        "Spider",
        "Siege",
        "Sanguine",
        "Bear",
        "Hound",
        "Phoenix",
        "Dragon",
        "Lion",
        "Gorilla",
        "Rhino",
        "Storm",
        "Shadow",
        "Nocturn",
        "Prime",
        "Zeus",
        "Essence",
        "Banshee",
        "Specter",
        "Typhoon",
        "Pinnacle",
        "Odin",
        "Silver",
        "Platinum",
        "Titan",
        "Heart",
        "Karma",
        "Angel",
        "Demon",
        "Arcane",
        "Mystic",
        "Jupiter",
        "Mars",
        "Meridian",
        "Atlas",
        "Raptor",
        "Void",
        "Hurricane",
        "Harbor",
        "Cold",
        "Jet",
        "Global",
        "Green",
        "Red",
        "Blue",
        "Tap",
        "Soul",
        "Slick",
        "Omen",
        "Arm",
        "Revelation",
        "Twilight",
        "Quad",
        "Tri",
        "Saturn",
        "Ward",
        "Violet",
        "Minutemen",
        "Steel",
        "Granite",
        "Stone",
        "Slate",
        "First",
        "Federal",
        "Statement",
        "Macguffin",
        "United",
        "King",
        "Queen",
        "Sultan",
        "Atom",
        "Cellular",
        "Spruce",
        "Black",
        "Executive",
        "Admin"
    ]

    ngin = NGIN( mission_struct, madlibs )

    ngin.start()



if __name__ == '__main__':
    main()

