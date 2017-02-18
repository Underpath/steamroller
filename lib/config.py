import ConfigParser
import os
from sys import exit

CONFIG_FILE = 'config/config.cfg'

def get_steam_id():
    return config.get('Steam', 'STEAM_ID')

    
def get_steam_api_key():
    return config.get('Steam', 'API_KEY')

    
def get_steam_api_url():
    return config.get('Steam', 'API_URL')

    
def get_excluded_appids():
    exclusions = config.get('Steam', 'EXCLUDE')
    return map(int, exclusions.split(','))

    
def get_included_appids():
    inclusions = config.get('Steam', 'INCLUDE')
    return map(int, inclusions.split(','))

    
def get_steam_determiners():
    determiners = config.get('Steam', 'DETERMINERS')
    return determiners.split(',')


def generate_config_file():
    # Default config values, mostly empty.
    config.add_section('Steam')
    config.set('Steam',"# Place your Steam API key here.")
    config.set('Steam','API_KEY','')
    config.set('Steam',"# Place your Steam ID here.")
    config.set('Steam','STEAM_ID','')
    config.set('Steam',"# Its unlikely this will need to change, but just in case.")
    config.set('Steam','API_URL','https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?')
    config.set('Steam',"# Games to be excluded from the draw.")
    config.set('Steam','EXCLUDE','')
    config.set('Steam',"# Games to be included that may have a platime of more than 0")
    config.set('Steam','INCLUDE','')
    config.set('Steam',"# Steam does not take determiners into account when sorting games, place here those you want to ignore when sorting games by title.")
    config.set('Steam','DETERMINERS','a,an,the')
    
    if not os.path.exists(os.path.dirname(CONFIG_FILE)):
        os.makedirs(os.path.dirname(CONFIG_FILE))    
    with open(CONFIG_FILE, 'w') as configuration_file:
        config.write(configuration_file)

config = ConfigParser.ConfigParser(allow_no_value=True)

if os.path.isfile(CONFIG_FILE):
    config.read(CONFIG_FILE)
else:
    print 'configuration file not found, generating sample configuration file at "config/config.cfg", please fill out the options and try running the program again.'
    generate_config_file()
    exit()