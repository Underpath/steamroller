import ConfigParser
import os

CONFIG_FILE = 'config/config.cfg'

def get_option(option,option_type='str'):
    if option_type == 'str':
        return config.get(get_section_name(), option)

    
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
    option['default_value'] = ''
    options.append(option)
    option = {}
    option['name'] = 'OWNED_GAMES_API'
    option['mandatory'] = True
    option['comment'] = "It's unlikely this will need to change, but just in case."
    option['default_value'] = 'https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?'
    options.append(option)
    option = {}
    option['name'] = 'VANITY_URL_TO_STEAMID_API'
    option['mandatory'] = True
    option['comment'] = "It's unlikely this will need to change, but just in case."
    option['default_value'] = 'http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?'
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
    option = {}
    option['name'] = 'STEAMCOMMUNITY_BASE_URL'
    option['mandatory'] = True
    option['comment'] = "Base URL for Steamcommunity's vanity URLs"
    option['default_value'] = 'https://steamcommunity.com/id'
    options.append(option)
    return options

def get_default_option(name):
    for option in get_config_file_options():
        if option['name'] == name:
            return option
    return False

config = ConfigParser.ConfigParser()
config.read(CONFIG_FILE)