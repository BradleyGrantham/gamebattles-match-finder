# Gamebattles cli

[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/)
[![Twitter Follow](https://img.shields.io/twitter/follow/espadrine.svg?style=social&label=Follow)](https://twitter.com/BradleyGrantham)

## Installation
For installation you will need 
[Python 3.6](https://www.python.org/downloads/release/python-360/) 
and [pip](https://pypi.org/project/pip/).

```bash
git clone https://github.com/BradleyGrantham/gamebattles-match-finder.git
cd gamebattles-match-finder
pip install .
```

## Set environment variables
To get the package working, you need to provide the a few details:
  * Your MLG email - `MLG_USER`
  * Your MLG password - `MLG_PASSWORD`
  * Your team id - `MLG_TEAM_ID`
  * The game your team plays - `MLG_GAME`
  * A specific session cookie - `MLG_COOKIE`
  
This need to be provided as environment variables. To set this, use `export` in
your terminal.
For example:
```bash
export MLG_USER=me@example.com
export MLG_PASSWORD=password
export MLG_TEAM_ID=00000000
export MLG_GAME=call-of-duty-black-ops-4
export MLG_COOKIE=0a1b2c3d4e5f6g
```

> If you want these to be available from session to session, it's best to add them
to you `.bash_profile`

### Finding your team id
To find your team id, navigate to your teams page. 
In the url bar you will see something similar to 
`http://gamebattles.majorleaguegaming.com/ps4/call-of-duty-black-ops-4/team/12345678`.
The last 8 digits are your team id. 

### Finding your cookie value
The cookie value we need is the one named `s8nhg2hs`. 
To find it, you need to login to gamebattles in your browser.
Once you're logged in, right click and click `Inspect`. Then in window that
appears, go to `Network`. With this open, navigate to the gamebattles homepage 
in your browser. 
In the `Network` bar, a list will start to appear. You want to click on the one
at the very top of this, the gamebattles home site, and then click on `Cookie`.
In the list of cookies that appears, copy the value of the `s8nhg2hs` cookie.
Save this in your environment with the `export` command as described above.
An example image of what you should expect to see is shown below.

![alt text](/images/cookie-img.png)

*This cookie will last for about two weeks before it needs to be refreshed.*

## Using the cli
To use the cli, use the command `gb` followed by your command. For example,
```bash
gb get-match
```

To get help at any point just use `--help`. For example,
```bash
gb --help
gb get-match --help
```

### Populate team details
Before you can get any matches you need to populate your team details. On 
the gamebattles API, every player in your team is mapped to a unique number
and it is this mapping that we need.

Once you have followed the above installation instructions, run the following
command to get your team mapping,
```bash
gb get-team-details
```
This will create a `.json` file with your mappings in. All gamertags are stored
as lowercase. This command will also print out the path at which these mappings
are saved.

### Get matches
To get a match use `get-match` command and follow it with the gamertags of the
players that are going to play (all in lowercase). For example, for a 3v3 game,
```bash
gb get-match player1 player2 player3
```
The player names that you type here have to match *exactly* that in the 
`player_mappings.json` (if you don't change anything, these will just be 
gamertags but all in lowercase).

> You can change the gamertags to anything you want in player_mappings.json.
For example, if somebody has a very long gamertag.

As there are many different types of matches you can get, there are many options
that you can type along with the `get-match` command. Those options are:
  * `--game-mode` - one of `sd` (Search and Destroy), `var` (Variant), `hp` 
  (Hardpoint) or `con` (Control). Default is `var`.
  * `--rule-set` - one of `cwl`, `gb` or `std` (for Standard). Default is `cwl`.
  * `--games` - this is the best of value, either `1`, `3` or `5`
  * `--keep-trying` - if `True` and there are no games available, it will
  retry every 5 seconds until it finds one, Default is `False`.
  
For example, if you wanted to get a GB Variant: Search and Destroy, best of 5, 
for 4 players and you wanted the program to keep searching until it found a 
game, you'd type
```bash
gb get-match player1 player2 player3 player4 --games 5 --rule-set gb --game-mode sd --keep-trying
```

### Reporting matches
You can only report your most recent match. To do this use
```bash
gb report
```
You can explicitly state whether you won with `--win` or `--no-win`. If you don't
explicitly state this, you will be prompted for an answer.

### Reporting your old match and getting a new one
If you want to report your old match and immediately get a new one you can use
```bash
gb report-and-get-new player1 player2 player3
```
This command takes the same arguments as both `report` and `get-match` combined.
