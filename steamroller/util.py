from math import ceil

from . import config


def paginate(section, my_games):
    """
    Function takes games and section and returns the games that would be
    displayed in that section after pagination.
    """

    games_in_section = []
    games_per_section = int(config.get_option("GAMES_PER_SECTION"))
    game_count = len(my_games)
    section_count = int(ceil(1.0 * game_count / games_per_section))

    if section > section_count:
        return False
    for i in range(games_per_section):
        try:
            games_in_section.append(my_games[i + ((section - 1) * games_per_section)])
        except IndexError:
            break

    pagination = {}

    pagination["links"] = pagination_links(section_count, section)

    pagination["game_count"] = game_count
    pagination["games"] = games_in_section
    pagination["section_count"] = section_count
    pagination["section"] = section
    return pagination


def pagination_links(section_count, section):
    """
    Generates the list of page numbers that will be linked when the
    pagination is rendered.
    """

    links = []
    if section_count <= 5:
        links = [i + 1 for i in range(section_count)]
    elif section_count >= 6:
        for i in range(section - 2, section + 3):
            links.append(i)
    while min(links) < 1:
        links = [i + 1 for i in links]
    while max(links) > section_count:
        links = [i - 1 for i in links]

    return sorted(links)
