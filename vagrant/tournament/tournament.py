#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
from psycopg2.extensions import AsIs

table_matches = "matches"
table_players = "players"

column_player_id = "id"
column_match_id = "id"
column_name = "name"
column_p1 = "p1"
column_p2 = "p2"
column_winner = "winner"

view_player_standings = "player_standings"


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def executeAndCloseConnection(statement, parameters):
    connection = connect()
    cursor = connection.cursor()
    cursor.execute(statement, parameters)
    closeConnection(connection)


def deleteMatches():
    """Remove all the match records from the database."""
    deleteTable(table_matches)


def deletePlayers():
    """Remove all the player records from the database."""
    deleteTable(table_players)


def countPlayers():
    """Returns the number of players currently registered."""
    return countOfRowsInTable(table_players)


def countMatches():
    """Returns the number of matches played."""
    return countOfRowsInTable(table_matches)


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    connection = connect()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO %s (%s) VALUES(%s);",
                   (AsIs(table_players), AsIs(column_name), name))
    closeConnection(connection)


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place,
    or a player tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    connection = connect()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM %s;", (AsIs(view_player_standings),))
    results = cursor.fetchall()
    closeConnection(connection)
    return results


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    connection = connect()
    cursor = connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO %s (%s,%s,%s) VALUES(%s, %s, %s);",
            (AsIs(table_matches),
             AsIs(column_p1), AsIs(column_p2), AsIs(column_winner),
             winner, loser, winner))
    except psycopg2.IntegrityError as e:
        print "ERROR: couldn't report match \n %s" % e
    closeConnection(connection)


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
    pairs = []

    # is that logic supposed to be inside SQL statement?
    for i in range(0, len(standings), 2):
        # takes adjacent players from standings and pack them into tuple
        player1 = standings[i]
        player2 = standings[i + 1]
        pairs.append((player1[0], player1[1], player2[0], player2[1]))

    return pairs


def closeConnection(connection):
    connection.commit()
    connection.close()


def deleteTable(tableName):
    executeAndCloseConnection("DELETE FROM %s;", (AsIs(tableName),))


def countOfRowsInTable(tableName):
    connection = connect()
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM %s;", (AsIs(tableName),))
    rowOne = cursor.fetchone()
    closeConnection(connection)
    return rowOne[0]
