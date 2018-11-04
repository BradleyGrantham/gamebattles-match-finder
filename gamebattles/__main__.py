import ast

import click
import requests
from bs4 import BeautifulSoup
import pandas as pd

from gamebattles.cookies import cookies
from gamebattles.team_details import team_details
from gamebattles.user_authentication import user_authentication
from gamebattles.report_form import report_form, report_config

PUT_URL = 'https://gb-api.majorleaguegaming.com/api/v1/challenges/{}/accept'

REPORT_URL = 'https://gb-api.majorleaguegaming.com/api/v1/matches/{}/report'


class MatchNotAccepted(Exception):
    pass


class NoGamesAvailable(Exception):
    pass


@click.group()
def cli():
    pass


def get_all_matches():
    with requests.Session() as sess:
        sess.post('https://accounts.majorleaguegaming.com/session', data=user_authentication)
        r = sess.get('http://gamebattles.majorleaguegaming.com/ps4/call-of-duty-black-ops-4/ladder/team-eu/match'
                     '-finder',
                     cookies=cookies)
    soup = BeautifulSoup(r.content)
    table = soup.find('table')
    df = pd.read_html(str(table))[0]
    try:
        df = assign_match_type_to_matches(df)
    except UnboundLocalError:
        raise NoGamesAvailable()
    df['Actions'] = [row.find_all('input')[1]['value'] for row in table.find_all('form')]
    return df


def assign_match_type_to_matches(df):
    for index, row in df.iterrows():
        if 'Matches' in row['Match Time']:
            current_type = row['Match Time'].split(' ')[0]
        else:
            df.set_value(index, 'Match Type', current_type)

    return df[df['Match Type'] == df['Match Type']]


def filter_matches(df, team_size='4v4', mapset='GB Variant: Search and Destroy', games=3):
    df = df[df['Match Time'] == 'Available Now']
    df = df[(df['Match Type'] == team_size) & (df['Mapset'] == mapset) & (df['Games'] == games)]

    if df.empty:
        raise NoGamesAvailable(', '.join([team_size, mapset, str(games)]))

    return df


def accept_match(match_id, team_id, roster, dryrun=False):
    accept_config = {'acceptingTeamId': int(team_id), 'maps': []}
    accept_config['roster'] = roster
    with requests.Session() as sess:
        sess.post('https://accounts.majorleaguegaming.com/session', data=user_authentication)
        sess.get('http://gamebattles.majorleaguegaming.com/ps4/call-of-duty-black-ops-4/ladder/team-eu/match-finder',
                 cookies=cookies)
        sess.options(PUT_URL.format(match_id), cookies=cookies)
        if not dryrun:
            match_response = sess.put(PUT_URL.format(match_id), json=accept_config)
            return match_response.content
        else:
            return [match_id, team_id, ';'.join([str(x) for x in roster])]


def pick_match_from_df(df, higher_rank=False):
    if higher_rank:
        pass
    else:
        return df['Actions'].values.tolist()[0]


def get_roster_from_player_names(players, player_dict):
    return [player_dict['team-members'][player] for player in players]


def get_match(players, mapset, games, team_id=None, dryrun=False):
    roster = get_roster_from_player_names(players, team_details)
    team_size = str(len(players)) + 'v' + str(len(players))
    df = get_all_matches()
    df = filter_matches(df, team_size=team_size, mapset=mapset, games=games)
    match_id = pick_match_from_df(df)
    if team_id is None:
        team_id = team_details['team-id']
    accept_match_response = accept_match(match_id, team_id, roster, dryrun=dryrun)
    print(accept_match_response)


def parse_match_response(match_response):
    if isinstance(match_response, list):
        return ', '.join(match_response)
    else:
        # TODO - getting value error for this now if match is successfully found
        return match_response


def get_most_recent(team_id=None):
    if team_id is None:
        team_id = team_details['team-id']
    r = requests.get('http://gamebattles.majorleaguegaming.com/ps4/call-of-duty-black-ops-4/team/{}'.format(team_id))
    soup = BeautifulSoup(r.content)
    table = soup.find_all('table')[1]
    rows = table.find_all('tr')
    for row in rows[1:]:
        if row.find_all('td')[4].text == 'Scheduled':
            opponent_id = row.find_all('td')[2].find('a')['href'].split('/')[-1]
            match_id = row.find_all('td')[5].find('a')['href'].split('=')[-1]
            return opponent_id, match_id


def report_most_recent(win, team_id=None):
    # TODO - should be able to handle best of 1

    if team_id is None:
        team_id = team_details['team-id']

    opponent_id, match_id = get_most_recent(team_id)

    if win:
        report_config['reportTeamStatus'] = 'WIN'
    else:
        report_config['reportTeamStatus'] = 'LOST'

    with requests.Session() as sess:
        sess.post('https://accounts.majorleaguegaming.com/session', data=user_authentication)
        sess.get('http://gamebattles.majorleaguegaming.com/ps4/call-of-duty-black-ops-4/ladder/team-eu/match-finder')
        payload = report_form.format(team_id=team_id, opponent_id=opponent_id, team_score=0,
                                     opponent_score=1, match_id=match_id)
        payload = ast.literal_eval(payload.split('\\')[0])
        sess.headers.update({'X-Origin': 'gamebattles-web'})
        sess.post('http://gamebattles.majorleaguegaming.com/ps4/call-of-duty-black-ops-4/team/{team_id}'
                  '/match?id={match_id}'.format(team_id=team_id, match_id=match_id), data=payload,
                  params={'id': match_id})
        sess.options(REPORT_URL.format(match_id))
        print(REPORT_URL.format(match_id))
        report_response = sess.post(REPORT_URL.format(match_id),
                                    json=report_config)
    print(report_response.content)


@cli.command(name='get-match')
@click.argument('players', nargs=-1)
@click.option('--mapset', default='GB Variant: Search and Destroy')
@click.option('--games', default=3)
@click.option('--team-id', default=None)
@click.option('--dryrun/--no-dryrun', default=False)
def cli_get_match(players, mapset, games, team_id, dryrun):
    get_match(players, mapset, games, team_id, dryrun)


@cli.command(name='report-and-get-new')
@click.argument('players', nargs=-1)
@click.option('--mapset', default='GB Variant: Search and Destroy')
@click.option('--games', default=3)
@click.option('--team-id', default=None)
@click.option('--dryrun/--no-dryrun', default=False)
@click.option('--win/--no-win', default=False)
def cli_report_and_get_new(players, win, mapset, games, team_id, dryrun):
    report_most_recent(win, team_id)
    get_match(players, mapset, games, team_id, dryrun)


@cli.command(name='report')
@click.option('--win/--no-win', default=False)
@click.option('--team-id', default=None)
def cli_report(win, team_id):
    report_most_recent(win, team_id)


if __name__ == '__main__':
    cli()
