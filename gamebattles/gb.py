"""This module contains all the main methods. __main__.py contains the cli"""

import datetime
import json
import time

from bs4 import BeautifulSoup
import pandas as pd
import pathlib2
import requests

import gamebattles.constants
import gamebattles.exceptions


def get_most_recent_match(team_id=None):
    if team_id is None:
        team_id = gamebattles.constants.TEAM_ID
    r = requests.get(gamebattles.constants.TEAM_URL
                     .format(game=gamebattles.constants.GAME, team_id=team_id))
    soup = BeautifulSoup(r.content)
    table = soup.find_all('table')[1]
    rows = table.find_all('tr')
    scheduled_matches = []
    times = []
    for row in rows[1:]:
        if row.find_all('td')[4].text == 'Scheduled':
            scheduled_matches.append(row)
            times.append(datetime.datetime.strptime(
                row.find_all('td')[1].text.split(' ')[0], '%H:%M').time()
                         )
    if scheduled_matches:
        times = [abs((datetime.datetime.now() -
                 datetime.datetime.combine(datetime.date.today(), tim))
                 .total_seconds())
                 for tim in times if tim]

        sorted_scheduled = [x for _, x in sorted(zip(times, scheduled_matches))]
        opponent_id = (sorted_scheduled[0]
                       .find_all('td')[2].find('a')['href'].split('/')[-1])
        match_id = (sorted_scheduled[0]
                    .find_all('td')[5].find('a')['href'].split('=')[-1])
        match_url = sorted_scheduled[0].find_all('a')[1].get('href')
        return opponent_id, match_id, match_url

    else:
        raise gamebattles.exceptions.NoMatchesToReport()


def report_most_recent(win, team_id=None):
    # TODO - should be able to handle best of 1 (I think it can?)

    if team_id is None:
        team_id = gamebattles.constants.TEAM_ID

    opponent_id, match_id, _ = get_most_recent_match(team_id)

    if win:
        gamebattles.constants.REPORT_CONFIG['reportTeamStatus'] = 'WON'
    else:
        gamebattles.constants.REPORT_CONFIG['reportTeamStatus'] = 'LOST'

    with requests.Session() as sess:
        sess.post(gamebattles.constants.SESSION_URL,
                  data=gamebattles.constants.USER_AUTHENTICATION)
        sess.get(gamebattles.constants.MATCH_FINDER_URL
                 .format(game=gamebattles.constants.GAME,
                         team_type=TEAM_DETAILS['team-type']))
        report_response = sess.post(gamebattles.constants.REPORT_URL
                                    .format(match_id=match_id),
                                    json=gamebattles.constants.REPORT_CONFIG)
    report_response = report_response.content.decode('utf-8')
    report_response = json.loads(report_response)
    # TODO - parse this properly
    print(report_response)


def check_team_details():
    global TEAM_DETAILS
    try:
        with open(gamebattles.constants.PLAYER_MAPPINGS_PATH, 'r') as f:
            TEAM_DETAILS = json.load(f)
    except FileNotFoundError as e:
        print("Make sure you have run the `populate-team-details` command")
        raise e


def get_all_matches():
    with requests.Session() as sess:
        r = sess.get(gamebattles.constants.MATCH_FINDER_URL.
                     format(game=TEAM_DETAILS['game'],
                            team_type=TEAM_DETAILS['team-type']),
                     cookies=gamebattles.constants.COOKIES)
    soup = BeautifulSoup(r.content)
    table = soup.find('table')
    df = pd.read_html(str(table))[0]
    try:
        df = assign_match_type_to_matches(df)
    except UnboundLocalError:
        raise gamebattles.exceptions.NoGamesAvailable()
    df['Actions'] = [row.find_all('input')[1]['value']
                     for row in table.find_all('form')]
    return df


def assign_match_type_to_matches(df):
    for index, row in df.iterrows():
        if 'Matches' in row['Match Time']:
            current_type = row['Match Time'].split(' ')[0]
        else:
            df.set_value(index, 'Match Type', current_type)

    return df[df['Match Type'] == df['Match Type']]


def filter_matches(df, team_size='4v4',
                   mapset='CWL Variant: Search and Destroy',
                   games=3):
    df = df[df['Match Time'] == 'Available Now']
    df = df[df['PremiumMatch 1'] == 'No']
    df = df[(df['Match Type'] == team_size) & (df['Mapset'] == mapset)
            & (df['Games'] == games)]

    if df.empty:
        raise gamebattles.exceptions.NoGamesAvailable(', '.join([team_size,
                                                                 mapset,
                                                                 str(games)]))

    return df


def accept_match(match_id, team_id, roster, dryrun=False):
    accept_config = dict()
    accept_config.update({'acceptingTeamId': int(team_id),
                          'maps': []})
    accept_config['roster'] = roster
    with requests.Session() as sess:
        sess.post(gamebattles.constants.SESSION_URL,
                  data=gamebattles.constants.USER_AUTHENTICATION)
        sess.get(gamebattles.constants.MATCH_FINDER_URL,
                 cookies=gamebattles.constants.COOKIES)
        sess.options(gamebattles.constants.ACCEPT_URL.format(match_id=match_id),
                     cookies=gamebattles.constants.COOKIES)
        if not dryrun:
            match_response = sess.put(gamebattles.constants.ACCEPT_URL
                                      .format(match_id=match_id),
                                      json=accept_config)
            return match_response.content
        else:
            # return [match_id, team_id, ';'.join([str(x) for x in roster])]
            return "{'DRYRUN': 'complete'}"


def pick_match_from_df(df, higher_rank=False):
    if higher_rank:
        pass
    else:
        return df['Actions'].values.tolist()[0]


def get_roster_from_player_names(players, player_dict):
    return [player_dict['team-members'][player] for player in players]


def get_match(players, rule_set, game_mode, games, team_id=None, dryrun=False,
              keep_trying=False):
    roster = get_roster_from_player_names(players,
                                          TEAM_DETAILS)
    team_size = str(len(players)) + 'v' + str(len(players))
    mapset = combine_rule_set_and_game_mode(rule_set, game_mode)
    df = None
    if keep_trying:
        while df is None:
            try:
                df = get_all_matches()
                df = filter_matches(df, team_size=team_size, mapset=mapset,
                                    games=games)
            except gamebattles.exceptions.NoGamesAvailable:
                print('No matches yet, retrying in 5 seconds...')
                df = None
                time.sleep(5)
    else:
        df = get_all_matches()
        df = filter_matches(df, team_size=team_size, mapset=mapset, games=games)

    match_id = pick_match_from_df(df)
    if team_id is None:
        team_id = gamebattles.constants.TEAM_ID
    accept_match_response = accept_match(match_id, team_id,
                                         [int(x) for x in roster],
                                         dryrun=dryrun)

    accept_match_response = json.loads(accept_match_response.decode('utf-8'))
    if accept_match_response['errors']:
        print(accept_match_response['errors'])
        raise gamebattles.exceptions.MatchFoundButCouldntAccept

    _, _, url = get_most_recent_match()

    r = requests.get(url)
    soup = BeautifulSoup(r.content)
    maps_df = pd.read_html(str(soup.find_all('table')[2]))[0]
    rosters = soup.find_all("div", {"class": "roster"})
    team1 = [x.text for x in rosters[0].find_all('a', {'target': '_new'})]
    team2 = [x.text for x in rosters[1].find_all('a', {'target': '_new'})]
    print_match_details(maps_df, team1, team2)


def combine_rule_set_and_game_mode(rule_set, game_mode):
    rule_set = gamebattles.constants.RULE_SETS[rule_set]
    game_mode = gamebattles.constants.GAME_MODES[game_mode]
    if game_mode:
        mapset = ': '.join([rule_set, game_mode])
        return mapset
    else:
        return rule_set


def print_match_details(maps_df, team1, team2):
    print('\n\n')
    print(maps_df[1:].to_string(header=None, index=False))
    print('\n')
    print('Rosters')
    for t1, t2 in zip(team1, team2):
        print(t1, t2)
    print('\n\n')


def get_player_mappings():
    df = None
    while df is None:
        try:
            df = gamebattles.gb.get_all_matches()
        except gamebattles.exceptions.NoGamesAvailable:
            time.sleep(5)
    match_id = df['Actions'].tolist()[0]
    form_data = {'challenge_id': match_id, 'do': 'Accept', 'grant': 'w'}
    r = requests.post(
        gamebattles.constants.MATCH_FINDER_URL.format(
            game=gamebattles.constants.GAME,
            team_type=TEAM_DETAILS['team-type']), data=form_data,
        cookies=gamebattles.constants.COOKIES)
    soup = BeautifulSoup(r.content)
    df = pd.read_html(str(soup.find_all('form')[0].find('table')))[0]
    player_names = [x.lower() for x in df[3].tolist()[1:]]
    player_ids = [x.get('value')
                  for x in soup.find_all('input', {'name': 'roster[]'})]
    return dict(zip(player_names, player_ids))


def get_team_details():
    global TEAM_DETAILS
    TEAM_DETAILS = {}
    r = requests.get(gamebattles.constants.TEAM_URL)
    soup = BeautifulSoup(r.content)
    TEAM_DETAILS['game'] = gamebattles.constants.GAME
    TEAM_DETAILS['team-type'] = (
        soup.find('div', {'class': 'boxOuter xl lt clr'})
            .find_all('a')[-1].get('href').split('/')[-1]
    )
    player_mappings = gamebattles.gb.get_player_mappings()
    TEAM_DETAILS['team-members'] = player_mappings

    with open(gamebattles.constants.PLAYER_MAPPINGS_PATH, 'w') as f:
        json.dump(TEAM_DETAILS, f)

    print('Player mappings saved at: {path}'.format(
          path=gamebattles.constants.PLAYER_MAPPINGS_PATH))
