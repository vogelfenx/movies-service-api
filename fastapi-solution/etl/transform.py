import json
from config import elastic_conf

def transformer(transformed_batch: list) -> list:

    es_batch = []

    for film in transformed_batch:

        director = []
        actors = []
        actor_names = []
        writers = []
        writer_names = []

        for person in film.persons:
            if person['person_role'] == 'director':
                director.append(person['person_name'])
            elif person['person_role'] == 'actor':
                actors.append({
                    'id': str(person['person_id']),
                    'name': person['person_name']}
                    )
                actor_names.append(person['person_name'])
            elif person['person_role'] == 'writer':
                writers.append({
                    'id': str(person['person_id']),
                    'name': person['person_name']}
                )
                writer_names.append(person['person_name'])

        action = {
            '_index': elastic_conf.index_name,
            '_id': str(film.id),
            'id': str(film.id),
            'imdb_rating': film.imdb_rating,
            'genre': film.genres,
            'title': film.title,
            'description': film.description,
            'director': director,
            'actors_names': actor_names,
            'writers_names': writer_names,
            'actors': actors,
            'writers': writers,
        }

        yield action

    return es_batch


if __name__ == '__main__':
    pass
