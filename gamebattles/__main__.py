import click
import warnings
warnings.filterwarnings("ignore")

import gamebattles.gb as gb


@click.group()
def cli():
    pass


@cli.command(name='get-match')
@click.argument('players', nargs=-1)
@click.option('--rule-set', default='cwl')
@click.option('--game-mode', default='var')
@click.option('--games', default=3)
@click.option('--team-id', default=None)
@click.option('--dryrun/--no-dryrun', default=False)
@click.option('--keep-trying/--dont-keep-trying', default=False)
def cli_get_match(players, rule_set, game_mode, games, team_id, dryrun,
                  keep_trying):
    gb.check_team_details()
    gb.get_match(players,
                 rule_set,
                 game_mode,
                 games,
                 team_id,
                 dryrun,
                 keep_trying)


@cli.command(name='report-and-get-new')
@click.argument('players', nargs=-1)
@click.option('--rule-set', default='cwl')
@click.option('--game-mode', default='var')
@click.option('--games', default=3)
@click.option('--team-id', default=None)
@click.option('--dryrun/--no-dryrun', default=False)
@click.option('--win/--no-win', default=False)
@click.option('--keep-trying/--dont-keep-trying', default=False)
def cli_report_and_get_new(players, win, rule_set, game_mode, games, team_id,
                           dryrun, keep_trying):
    gb.check_team_details()
    gb.report_most_recent(win, team_id)
    gb.get_match(players,
                 rule_set,
                 game_mode,
                 games,
                 team_id,
                 dryrun,
                 keep_trying)


@cli.command(name='report')
@click.option('--win/--no-win', prompt=True, default=False)
@click.option('--team-id', default=None)
def cli_report(win, team_id):
    gb.check_team_details()
    gb.report_most_recent(win, team_id)


@cli.command(name='get-team-details')
def cli_populate_team_details():
    gb.get_team_details()


if __name__ == '__main__':
    cli()
