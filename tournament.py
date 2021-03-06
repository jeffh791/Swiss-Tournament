#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2

'''Database name = tournament   tables = players, matches
players schema = (id serial primary key not null, name text not null)
matches schema = (match_id serial primary key not null, winner int not null,
    loser int not null, winner_score int, loser_score int)
'''

def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")

def deleteMatches():
    """Remove all the match records from the database."""
    DB = connect()
    c = DB.cursor()
    c.execute("DELETE FROM matches;")
    c.execute("ALTER SEQUENCE matches_match_id_seq restart;") #required to restart id at 1
    DB.commit()
    DB.close()

def deletePlayers():
    """Remove all the player records from the database."""
    DB = connect()
    c = DB.cursor()
    c.execute("DELETE FROM players;")
    c.execute("ALTER SEQUENCE players_id_seq restart;") #required to restart id at 1
    DB.commit()
    DB.close()

def countPlayers():
    """Returns the number of players currently registered."""
    DB = connect()
    c = DB.cursor()
    c.execute("SELECT count(id) FROM players;")
    count = c.fetchone()[0]
    DB.close()
    return count

def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    DB = connect()
    c = DB.cursor()
    c.execute("INSERT INTO players VALUES(DEFAULT, %s);", (name,))
    DB.commit()
    DB.close()

def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    DB = connect()
    c = DB.cursor()
    query = """ SELECT id, name,
                    COUNT(CASE id WHEN winner THEN 1 ELSE NULL END) AS wins,
                    COUNT(match_id) AS matches_played
                FROM players
                LEFT JOIN matches ON id IN (winner, loser)
                GROUP BY id, name
                ORDER BY wins DESC; """
    # CASE/WHEN/THEN/END is same as IF/ELSE statement in programming languages
    # Join matches onto players table where id matches either winner or loser column.
    # Group by name and id
    # then COUNT() all match_id from this join and output as matches_played
    c.execute(query)
    standings = c.fetchall()
    DB.close()
    return standings

def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    DB = connect()
    c = DB.cursor()
    query = "INSERT INTO matches(winner, loser) VALUES(%s, %s);"
    c.execute(query, (int(winner), int(loser)))
    DB.commit()
    DB.close()
 
def swissPairings():
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
  
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    standings = playerStandings()
    draws = []
    pairs = []
    count = 0
    for x in standings:
        if (count%2 == 0):
            pairs = []              #clear pairs list
            pairs.append(x[0])      #append id and name of one player
            pairs.append(x[1])
        else:
            pairs.append(x[0])      #append id and name of other player
            pairs.append(x[1])
            draws.append(pairs)     #pairs of players appended into draws
        count = count + 1
    return draws

