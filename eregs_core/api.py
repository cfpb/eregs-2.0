from utils import *


def meta_api(version=None, eff_date=None, meta_tag='preamble'):

    if version is not None and eff_date is not None:
        node_id = ':'.join([version, eff_date, meta_tag])
        data = meta.find_one({'node_id': {'$regex': node_id}})
        del data['_id']
    elif version is not None:
        node_id = version
        data = meta.find({'node_id': {'$regex': node_id}, 'tag': meta_tag})
    else:
        node_id = '.*'
        data = meta.find({'node_id': {'$regex': node_id}, 'tag': meta_tag})

    if node_id == version or node_id == '.*':
        return_data = []
        for item in data:
            if isinstance(item, dict) and '_id' in item:
                del item['_id']
            return_data.append(item)
    else:
        return_data = data

    # gotta return as a dict, not a pymongo cursor
    return return_data


def toc_api(version=None, eff_date=None):

    if version is not None and eff_date is not None:
        node_id = ':'.join([version, eff_date] + ['tableOfContents'])
        data = get_with_descendants(toc, node_id)

        return data

    return {}