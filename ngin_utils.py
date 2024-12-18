import json, os, platform, sys, pprint, random
from typing import *

DEBUG = False

MAX_ADJACENT_LOCATIONS = 6
WORLD_GEN_STICKINESS = 0.4
WORLD_GEN_SUBLOCATION_CHANCE = 0.3
WORLD_GEN_POPULATION_GROUP_CHANCE = 0.25


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

