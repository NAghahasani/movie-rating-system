-- seeddb.sql
BEGIN;

-- 1. Cleanup
DELETE FROM movie_ratings; DELETE FROM movie_genres; DELETE FROM movies; DELETE FROM directors; DELETE FROM genres;
ALTER SEQUENCE directors_id_seq RESTART WITH 1;
ALTER SEQUENCE genres_id_seq RESTART WITH 1;
ALTER SEQUENCE movies_id_seq RESTART WITH 1;
ALTER SEQUENCE movie_ratings_id_seq RESTART WITH 1;

-- 2. Staging
DROP TABLE IF EXISTS tmdb_movies_raw CASCADE; DROP TABLE IF EXISTS tmdb_credits_raw CASCADE; DROP TABLE IF EXISTS tmdb_selected CASCADE;

CREATE TABLE tmdb_movies_raw (
    budget NUMERIC, genres TEXT, homepage TEXT, id INTEGER PRIMARY KEY, keywords TEXT, original_language TEXT, original_title TEXT, overview TEXT, popularity NUMERIC, production_companies TEXT, production_countries TEXT, release_date TEXT, revenue NUMERIC, runtime NUMERIC, spoken_languages TEXT, status TEXT, tagline TEXT, title TEXT, vote_average NUMERIC, vote_count INTEGER
);

CREATE TABLE tmdb_credits_raw ( movie_id INTEGER, title TEXT, "cast" TEXT, crew TEXT );

-- 4. Load from /tmp/ inside container
\copy tmdb_movies_raw FROM '/tmp/tmdb_5000_movies.csv' CSV HEADER;
\copy tmdb_credits_raw (movie_id, title, "cast", crew) FROM '/tmp/tmdb_5000_credits.csv' CSV HEADER;

-- 5. Genres
INSERT INTO genres (name, description)
SELECT DISTINCT trim(g->>'name'), 'Imported from TMDB'
FROM tmdb_movies_raw m, LATERAL jsonb_array_elements(m.genres::jsonb) AS g
WHERE g->>'name' IS NOT NULL ORDER BY 1;

-- 6. Directors (Fixed type casting for birth_year)
INSERT INTO directors (name, birth_year, description)
SELECT DISTINCT trim(c->>'name'), CAST(NULL AS INTEGER), 'Imported from TMDB'
FROM tmdb_credits_raw cr, LATERAL jsonb_array_elements(cr.crew::jsonb) AS c
WHERE c->>'job' = 'Director' AND c->>'name' IS NOT NULL ORDER BY 1;

-- 7. Staging 1000
CREATE TABLE tmdb_selected AS
WITH joined AS (
    SELECT m.id AS tmdb_id, m.title, m.genres, m.release_date, m.vote_average, m.vote_count, m.popularity, cr."cast", cr.crew,
    (SELECT c2->>'name' FROM jsonb_array_elements(cr.crew::jsonb) c2 WHERE c2->>'job' = 'Director' LIMIT 1) AS director_name
    FROM tmdb_movies_raw m JOIN tmdb_credits_raw cr ON cr.movie_id = m.id
),
filtered AS (
    SELECT *, row_number() OVER (ORDER BY vote_count DESC, popularity DESC) AS rn FROM joined WHERE director_name IS NOT NULL
)
SELECT * FROM filtered WHERE rn <= 1000;

-- 8. Movies
INSERT INTO movies (title, director_id, release_year, "cast", description)
SELECT s.title, d.id, COALESCE(NULLIF(split_part(s.release_date, '-', 1), '')::INT, 2000),
(SELECT string_agg(cn, ', ') FROM (SELECT (c_el->>'name') AS cn FROM jsonb_array_elements(s."cast"::jsonb) AS c_el LIMIT 3) AS sub),
'Imported metadata' FROM tmdb_selected s JOIN directors d ON d.name = s.director_name;

-- 9. Movie Genres
INSERT INTO movie_genres (movie_id, genre_id)
SELECT mv.id, g.id FROM movies mv JOIN tmdb_selected s ON mv.title = s.title
JOIN LATERAL jsonb_array_elements(s.genres::jsonb) AS gj ON TRUE JOIN genres g ON g.name = gj->>'name' GROUP BY mv.id, g.id;

-- 10. Ratings
INSERT INTO movie_ratings (movie_id, score, rated_at)
SELECT m.id, (floor(random() * 10) + 1)::INT, now() - (random() * interval '5 years')
FROM movies m, LATERAL generate_series(1, (1 + floor(random() * 40))::INT);

COMMIT;