import os

import pathlib2

COOKIES = {
    's8nhg2hs': os.environ['MLG_COOKIE']
}

TEAM_ID = os.environ['MLG_TEAM_ID']

USER_AUTHENTICATION = {'login': os.environ['MLG_USER'],
                       'password': os.environ['MLG_PASSWORD']}

GAME = os.environ['MLG_GAME']

REPORT_CONFIG = {'loser': 0,
                 'reportTeamStatus': '',
                 'winner': 2
                 }

SESSION_URL = 'https://accounts.majorleaguegaming.com/session'

MATCH_FINDER_URL = "http://gamebattles.majorleaguegaming.com/ps4/{game}/" \
                   "ladder/{team_type}/match-finder"

ACCEPT_URL = "https://gb-api.majorleaguegaming.com/api/v1/challenges/" \
             "{match_id}/accept"

REPORT_URL = "https://gb-api.majorleaguegaming.com/api/v1/matches/" \
             "{match_id}/report"

TEAM_URL = ("http://gamebattles.majorleaguegaming.com/ps4/{game}/team/{team_id}"
            .format(game=GAME, team_id=TEAM_ID)
            )


GAME_MODES = {'sd': 'Search and Destroy',
              'hp': 'Hardpoint',
              'con': 'Control',
              'var': ''}

RULE_SETS = {'cwl': 'CWL Variant',
             'gb': 'GB Variant',
             'std': 'Standard'}

GB_DIR = pathlib2.Path("~/.gamebattles").expanduser()
PLAYER_MAPPINGS_PATH = GB_DIR / pathlib2.Path('player_mappings.json')

if not GB_DIR.exists():
    GB_DIR.mkdir()
