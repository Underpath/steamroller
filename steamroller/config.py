import configparser
import logging
import os

CONFIG_FILE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "config/config.cfg")
)
config = configparser.ConfigParser()
config.read(CONFIG_FILE)


def get_option(option, option_type=None):
    """
    Grabs the value of the option from the config file and returns it in the
    format requested.
    """

    if option_type == "bool":
        option_value = config.getboolean(get_section_name(), option)
    else:
        option_value = config.get(get_section_name(), option)
        if option_type == "str_list":
            option_value = option_value.split(",")
        elif option_type == "int_list":
            option_value = map(int, option_value.split(","))
    return option_value


def get_section_name():
    return "Steam"


def get_config_file_options():
    """
    Default config file options.
    """

    options = []
    option = {}
    option["name"] = "STEAM_ID"
    option["mandatory"] = True
    option["comment"] = "Place your Steam ID here."
    option["default_value"] = ""
    options.append(option)
    option = {}
    option["name"] = "STEAM_API_KEY"
    option["mandatory"] = True
    option["comment"] = "Place your Steam API key here."
    option["default_value"] = ""
    options.append(option)
    option = {}
    option["name"] = "OWNED_GAMES_API"
    option["mandatory"] = True
    option["comment"] = "It's unlikely this will need to change, but just" + " in case."
    option["default_value"] = (
        "https://api.steampowered.com/" + "IPlayerService/GetOwnedGames/v0001/"
    )
    options.append(option)
    option = {}
    option["name"] = "VANITY_URL_TO_STEAMID_API"
    option["mandatory"] = True
    option["comment"] = "It's unlikely this will need to change, but just in case."
    option["default_value"] = (
        "http://api.steampowered.com/ISteamUser/" + "ResolveVanityURL/v0001/"
    )
    options.append(option)
    option = {}
    option["name"] = "EXCLUDE"
    option["mandatory"] = False
    option["comment"] = "Games to be excluded from the draw."
    option["default_value"] = ""
    options.append(option)
    option = {}
    option["name"] = "INCLUDE"
    option["mandatory"] = False
    option["comment"] = (
        "Games to be included in the draw that may have a playtime of more than '0'."
    )
    option["default_value"] = ""
    options.append(option)
    option = {}
    option["name"] = "DETERMINERS"
    option["mandatory"] = False
    option["comment"] = (
        "Steam does not take determiners into account when sorting games by title, place here the determiners you want ignored when sorting games by title."
    )
    option["default_value"] = "a,an,the"
    options.append(option)
    option = {}
    option["name"] = "STEAMAPP_DETAILS_API"
    option["mandatory"] = True
    option["comment"] = "Base URL for retrieving information on a Steam APPID."
    option["default_value"] = "http://store.steampowered.com/api/appdetails"
    options.append(option)
    option = {}
    option["name"] = "STEAM_USER_INFO_API"
    option["mandatory"] = True
    option["comment"] = "Base URL for retrieving information on a Steam ID."
    option["default_value"] = (
        "http://api.steampowered.com/ISteamUser/" + "GetPlayerSummaries/v0001/"
    )
    options.append(option)
    option = {}
    option["name"] = "PCGW_API"
    option["mandatory"] = True
    option["comment"] = "Base URL for reaching the PCGamingWiki API."
    option["default_value"] = "http://pcgamingwiki.com/w/api.php"
    options.append(option)
    option = {}
    option["name"] = "DATABASE_PATH"
    option["mandatory"] = True
    option["comment"] = "Path to the DB."
    option["default_value"] = "steamroller/Data/app.db"
    options.append(option)
    option = {}
    option["name"] = "USER_REFRESH_TIME"
    option["mandatory"] = True
    option["comment"] = (
        "How much time must pass in seconds before a user's games are fetched again from Steam instead of the local DB. Default 10 mins."
    )
    option["default_value"] = "600"
    options.append(option)
    option = {}
    option["name"] = "GAME_REFRESH_TIME"
    option["mandatory"] = True
    option["comment"] = (
        "How much time must pass in seconds before a game's attributes are updated from Steam instead of the local DB. Default 1 day."
    )
    option["default_value"] = "86400"
    options.append(option)
    return options


def get_default_option(name):
    """
    Returns one of the options from the default options and its default values.
    """

    for option in get_config_file_options():
        if option["name"] == name:
            return option
    return False


class Flask_config:
    """
    Stores the configuration for flask.
    """

    WTF_CSRF_ENABLED = True
    SESSION_COOKIE_HTTPONLY = True
    SECRET_KEY = get_option("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = get_option("DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_TYPE = get_option("SESSION_TYPE")
    if get_option("TEST", "bool"):
        DEBUG = True
        STATIC_URL = None
    else:
        DEBUG = False
        STATIC_URL = get_option("STATIC_URL")


def get_log_handler():
    if get_option("TEST"):
        logging_level = "DEBUG"
    else:
        logging_level = get_option("LOGGING_LEVEL")
    formatter = logging.Formatter(
        "%(asctime)s;%(client_ip)s;%(filename)s:%(lineno)d;%(levelname)s;%(message)s"
    )

    handler = logging.StreamHandler()
    logging.getLogger().setLevel(logging_level)
    handler.setLevel(logging_level)
    handler.setFormatter(formatter)
    return handler
