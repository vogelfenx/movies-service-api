create schema if not exists content
;

create table if not EXISTS content.film_work (
    id uuid PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    creation_date DATE,
    rating float,
    type TEXT not null,
    created timestamp with time zone,
    modified timestamp with time zone
);

CREATE INDEX film_work_creation_date_idx ON content.film_work(creation_date)
;



CREATE TABLE IF NOT EXISTS content.person (
    id uuid PRIMARY KEY,
    full_name TEXT NOT NULL,
    created timestamp with time zone,
    modified timestamp with time zone
);


CREATE UNIQUE INDEX person_full_name_idx ON content.person(full_name);



CREATE TABLE IF NOT EXISTS content.person_film_work (
    id uuid PRIMARY KEY,
    film_work_id uuid NOT NULL REFERENCES content.film_work (id) ON DELETE CASCADE,
    person_id uuid NOT NULL REFERENCES content.person (id) ON DELETE CASCADE,
    role TEXT NOT NULL,
    created timestamp with time zone
);

CREATE UNIQUE INDEX film_work_person_idx ON content.person_film_work (film_work_id, person_id, role)
;



CREATE TABLE IF NOT EXISTS content.genre (
    id uuid PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    created timestamp with time zone,
    modified timestamp with time zone
);



CREATE TABLE IF NOT EXISTS content.genre_film_work (
    id uuid,
    genre_id uuid NOT NULL REFERENCES content.genre (id) ON DELETE CASCADE,
    film_work_id uuid NOT NULL REFERENCES content.film_work ON DELETE CASCADE,
    created timestamp with time zone
);

CREATE UNIQUE INDEX genre_film_work_idx on content.genre_film_work(film_work_id, genre_id)
;