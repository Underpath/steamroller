import ConfigParser
import config as steamroller_config
import os
import sys

def no_config_file(config_file_path):
    print 'Configuration file not found, generating sample configuration file at "config/config.cfg", please fill out the options and try running the program again.'
    generate_config_file(config_file_path)
    sys.exit()

def generate_config_file(config_file_path):
    # Default config values, mostly empty.
    config = ConfigParser.RawConfigParser(allow_no_value=True)
    config.optionxform = str
    section = steamroller_config.get_section_name()
    config.add_section(section)
    options = steamroller_config.get_config_file_options()
    for option in options:
        comment = '\n# ' + option['comment']
        config.set(section,comment)
        config.set(section,option['name'],option['default_value'])

    if not os.path.exists(os.path.dirname(config_file_path)):
        os.makedirs(os.path.dirname(config_file_path))
    with open(config_file_path, 'w') as configuration_file:
        config.write(configuration_file)

def check_config_file(config_file_path):
    # Checks that the config file exists and has the minimum requirements.
    if not os.path.isfile(config_file_path):
        no_config_file(config_file_path)
    
    config = ConfigParser.ConfigParser()
    missing_options = []
    missing_section = False
    section = steamroller_config.get_section_name()
    required_options = []
    options = steamroller_config.get_config_file_options()
    for option in options:
        if option['mandatory']:
            required_options.append(option['name'])
    try:
        config.read(config_file_path)
    except ConfigParser.MissingSectionHeaderError:
        missing_section = True
    for option in required_options:
        try:
            value = config.get(section, option)
            if not value:
                missing_options.append(option)
        except ConfigParser.NoSectionError:
            missing_section = True
        except ConfigParser.NoOptionError:
            missing_options.append(option)
    if missing_section:
        print 'Error: Section "' + section + '" not found in config file.'
        return False
    if missing_options:
        print '\nFollowing mandatory options missing from config file:\n'
        for option in missing_options:
            print '\t' + option
        print ''
        return False
    return True