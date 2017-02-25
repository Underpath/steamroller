# steamroller

## About

Get rid of the burden of having to pick which game in your Steam library you want to play next by having Steamroller pick for you!

## Requirements

* Steam API key, to get one go to https://steamcommunity.com/dev/apikey
* Steam ID, this is your Steam ID; you can get it using steamroller but you'll need your Steam vanity URL.

## Dependencies

* requests

## Usage

```
usage: steamroller.py [-a] [-g] [-h] [-i] [-l] [-s http://steamcommunity.com/id/<username>]

optional arguments:
  -a, --all             Choose from all games
  -g, --config          Generate basic config file.
  -h, --help            Show this help message and exit.
  -i, --list-all        List all games with their appid.
  -l, --list            List new games with their appid.
  -s http://steamcommunity.com/id/<username>, --steam-id http://steamcommunity.com/id/<username>
                        Returns the steam ID for the user of a given
                        steamcommunity URL.
```