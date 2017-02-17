import ConfigParser
import os

config = ConfigParser.ConfigParser()
config.read('config/config.cfg')

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