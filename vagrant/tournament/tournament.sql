-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

DROP DATABASE IF EXISTS tournament;

CREATE DATABASE tournament;
\c tournament;

CREATE TABLE players (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL
);

CREATE TABLE matches (
  id SERIAL PRIMARY KEY,
  p1 INT REFERENCES Players(id),
  p2 INT REFERENCES Players(id),
  winner INT REFERENCES Players(id),
  CONSTRAINT winner_is_p1_or_p2 CHECK(winner = p1 OR winner = p2),
  CONSTRAINT p1_is_not_p2 CHECK(p1 != p2)
);

CREATE VIEW number_of_matches AS
  SELECT players.id AS player_id, players.name, COUNT(matches.id) AS matches_count
    FROM players
      LEFT JOIN matches ON matches.p1 = players.id OR matches.p2 = players.id
         GROUP BY players.id;

CREATE VIEW number_of_wins AS
  SELECT players.id AS player_id, players.name, COUNT(matches.id) AS wins_count
    FROM players
      LEFT JOIN matches ON matches.winner = players.id
        GROUP BY players.id;

CREATE VIEW player_standings AS
  SELECT number_of_wins.*, number_of_matches.matches_count FROM number_of_wins
    INNER JOIN number_of_matches ON number_of_wins.player_id = number_of_matches.player_id
    ORDER BY wins_count DESC;