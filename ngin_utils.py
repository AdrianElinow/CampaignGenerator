import json, os, platform, sys, pprint, random
from typing import *

DEBUG = True

MAX_ADJACENT_LOCATIONS = 6
WORLD_GEN_STICKINESS = 0.4
WORLD_GEN_SUBLOCATION_CHANCE = 0.3
WORLD_GEN_POPULATION_GROUP_CHANCE = 0.25



def debug(*args):
    if not DEBUG:
        return

    for msg in args:
        print(f"[DEBUG] {msg}")


def save_json_to_file( filename: str, data, filepath : str =None, pretty: bool =False):
    if not filename:
        raise ValueError("filename cannot be null/empty")

    if not filepath:
        filepath = os.getcwd()

    absolute_path = f"{filepath}/{filename}"

    try:

        json_serialized = json.dumps( data, indent=( 4 if pretty else None ) )

        with open(absolute_path,'w') as open_file:

            open_file.write( data )

    except TypeError as te:
        print(f"Error while writing to file | Unable to serialize data\n{te}")
    except Exception as e:
        print(f"Error while writing to file [{absolute_path}]\n{e}")


def load_json_from_file( filename: str, filepath : str =None ):

    if not filename:
        raise ValueError("filename cannot be null/empty")

    if not filepath:
        filepath = os.getcwd()

    absolute_path = f"{filepath}/{filename}"

    if os.path.exists(absolute_path):

        try:

            with open(absolute_path,'r') as open_file:

                data = json.load( open_file )

                if data:
                    if DEBUG:
                        print(f"loaded [{absolute_path}]")

                    return data

        except json.JSONDecodeError as e:
            print(f"Error while parsing file [{absolute_path}]\n{e}")

    else:
        print(f"No file found at {absolute_path}")

    return None




def user_choice(user_options, literal=False, random_opt=False ):
        ''' Present user with available options, and allow them to pick
                an option to proceed. 

            literal : does the user need to type out the option explicitly?
                True -> user must enter the explicit option as typed.
                False -> user will instead enter the option's presented index
            random_opt : allow the user to select 'random' which will randomly
                select an option instead?
        '''

        choice = None
        chosen = None

        if literal:

            while not choice:
                choice = input(' / '.join(user_options)+'> ')

                for i, opt in enumerate(user_options):
                    if choice in opt:
                        if not chosen:
                            chosen = opt
                        else:
                            print('Multiple choice selected. Invalid')
                            choice = None
                            break
                if chosen:
                    return chosen
                choice = None
                print('Invalid')
        
        else:
            ''' Standard operation '''

            # preset options
            for i, opt in enumerate(user_options):
                # account for lists / tuples
                if type(opt) in [ type( (0,0) ), type( [1,1] ) ]: 
                    node_name, mission_type_tuple = opt
                    readable_description = "{0} {2} ({1})".format(mission_type_tuple[0], mission_type_tuple[1], node_name)

                    print('({0}) {1}'.format(i, readable_description))
                else: # simple items
                    print('({0}) {1}'.format(i, str(opt) ))
            if random_opt:
                print('({0}) {1}'.format(len(user_options), 'random'))

            # take user selection
            while not choice:
                try:
                    choice = input('(Choice) > ')
                    if choice in ['q','quit']:
                        raise KeyboardInterrupt

                    choice = int(choice)
                    if choice in range(len(user_options) + (1 if random_opt else 0)):
                        if choice == len(user_options):
                            chosen = random.choice(user_options)
                            return chosen

                        return user_options[choice]
                except ValueError as ve:
                    pass
                except KeyboardInterrupt as ki:
                    sys.exit(0) # account for Control-C exit
                choice = None
                print('Invalid')

        return choice

