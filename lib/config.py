import ConfigParser
import os
import config_file
from sys import exit

CONFIG_FILE = 'config/config.cfg'

def get_steam_id():
    return config.get(get_section_name(), 'STEAM_ID')

    
def get_steam_api_key():
    return config.get(get_section_name(), 'API_KEY')

    
def get_steam_api_url():
    return config.get(get_section_name(), 'API_URL')

    
def get_excluded_appids():
    exclusions = config.get(get_section_name(), 'EXCLUDE')
    return map(int, exclusions.split(','))

    
def get_included_appids():
    inclusions = config.get(get_section_name(), 'INCLUDE')
    return map(int, inclusions.split(','))

    
def get_steam_determiners():
    determiners = config.get(get_section_name(), 'DETERMINERS')
    return determiners.split(',')
    
def get_section_name():
    return 'Steam'

def get_config_file_options():
    options = []
    option = {}
    option['name'] = 'STEAM_ID'
    option['mandatory'] = True
    option['comment'] = "Place your Steam ID here."
    option['default_value'] = ''
    options.append(option)
    option = {}
    option['name'] = 'API_KEY'
    option['mandatory'] = True
    option['comment'] = "Place your Steam API key here."
    option['default_value'] = 'https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?'
    options.append(option)
    option = {}
    option['name'] = 'API_URL'
    option['mandatory'] = True
    option['comment'] = "It's unlikely this will need to change, but just in case."
    option['default_value'] = ''
    options.append(option)
    option = {}
    option['name'] = 'EXCLUDE'
    option['mandatory'] = False
    option['comment'] = "Games to be excluded from the draw."
    option['default_value'] = ''
    options.append(option)
    option = {}
    option['name'] = 'INCLUDE'
    option['mandatory'] = False
    option['comment'] = "Games to be included in the draw that may have a platime of more than '0'."
    option['default_value'] = ''
    options.append(option)
    option = {}
    option['name'] = 'DETERMINERS'
    option['mandatory'] = False
    option['comment'] = "Steam does not take determiners into account when sorting games by title, place here the determiners you want ignored when sorting games by title."
    option['default_value'] = 'a,an,the'
    options.append(option)
    return options


config = ConfigParser.ConfigParser()
config.read(CONFIG_FILE)