from urlparse import urlparse
import config
import config_file
import os
from urllib import urlencode
import requests

def get_steamid(url):
    config_file.check_config_file(config.CONFIG_FILE,[config.get_default_option('API_KEY')])
    config_file.check_config_file(config.CONFIG_FILE,[config.get_default_option('VANITY_URL_TO_STEAMID_API')])
    parsed_url = urlparse(url)
    parsed_steam_url = urlparse(config.get_option('STEAMCOMMUNITY_BASE_URL'))
    url_path = parsed_url.path.split('/')
    steam_url_path = parsed_steam_url.path.replace('/', '')
    is_steam_url = True
    
    if parsed_url.netloc != parsed_steam_url.netloc:
        is_steam_url = False
    elif len(url_path) != 3:
        is_steam_url = False
    elif url_path[1] != steam_url_path:
        is_steam_url = False
    elif not url_path[2]:
        is_steam_url = False
        
    if is_steam_url:
        params = {'key': config.get_option('API_KEY'), 'vanityurl': url_path[2], 'format': 'json'}
        api_url = config.get_option('VANITY_URL_TO_STEAMID_API')
        response = make_request_to_api(api_url,params)
        if response['success'] == 1:
            return response['steamid']
        else:
            print 'Steam ID not found.'
            return False
    else:
        print "This doesn't look like a Steamcommunity URL, please try again."

def make_request_to_api(base_url, params=None):
    if params:
        url = base_url +  urlencode(params)
    else:
        url = base_url
    r = requests.get(url)
    if r.status_code == 200:
        return r.json()['response']