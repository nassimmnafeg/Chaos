from collections import OrderedDict
import logging

def format_raw_disruption_history(raw_db_results):
    disruptions = OrderedDict()
    tags = {}

    for r in raw_db_results:
        disruption_id = r.id
        tag_id = r.tag_id

        disruption = {
            "internal_id": disruption_id,
            "id": r.public_id,
            "reference": r.reference,
            'note': r.note,
            'status': r.status,
            'version': r.version,
            'created_at': r.created_at,
            'updated_at': r.updated_at,
            'start_publication_date': r.start_publication_date,
            'end_publication_date': r.end_publication_date,
            'publication_status': '',
            'tags': [],
            'impacts': [],
            'properties': [],
            'localizations': []
        }

        if disruption_id not in tags:
            tags[disruption_id] = {}

        if tag_id :
            tags[disruption_id][tag_id] = {
                'id' : tag_id,
                'name' : r.tag_name,
                'created_at' : r.tag_created_at,
                'updated_at' : r.tag_updated_at
            }

        if disruption_id not in disruptions:
            disruptions[disruption_id] = disruption

    logging.getLogger(__name__).debug(tags)
    for disruption in disruptions.values():
        disruption_id = disruption['internal_id']
        if disruption_id in tags :
            disruption['tags'] = tags[disruption_id].values()

    return disruptions