import sys, os
from SimulaeCampaignGenerator import *


def main():
    
    # Import NGIN
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


    mission_struct = load_json_from_file( "NGIN/NGIN_config/story_struct.json" )
    ngin_settings = load_json_from_file( "NGIN/NGIN_config/ngin_settings.json" )

    save_file = None
    if len(sys.argv) >= 5:
        save_file = load_json_from_file( sys.argv[1] )

    # Setup 
    ngin = NGIN( mission_struct, ngin_settings, save_file )

    # Start

    try:

        ngin.start()

    except Exception as e:
        print(e)
    finally:
        print('saving...')
        ngin.save_to_file("save_file.json")


if __name__ == '__main__':
    main()