from math import ceil
from steamroller.lib import config


def paginate(section, my_games):
    games_in_section = []
    games_per_section = int(config.get_option('GAMES_PER_SECTION'))
    game_count = len(my_games)
    section_count = int(ceil(1.0 * game_count / games_per_section))

    if section > section_count:
        print section
        print section_count
        return False
    for i in range(games_per_section):
        try:
            games_in_section.append(my_games[i + ((section - 1) * games_per_section)])
        except IndexError:
            break

    pagination = {}
    
    if section_count <= 5:
        pagination['links'] = [i+1 for i in range(section_count)]



    pagination['game_count'] = game_count
    pagination['games'] = games_in_section
    pagination['section_count'] = section_count
    pagination['section'] = section
    return pagination
