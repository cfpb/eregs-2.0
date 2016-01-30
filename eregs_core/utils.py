import json
import os
import sys
import pdb

from collections import OrderedDict
from pymongo import MongoClient, ASCENDING
from lxml import etree
from pprint import pprint

client = MongoClient()
db = client['eregs']
regtext = db['regtext']
interps = db['interpretations']
toc = db['toc']
appendices = db['appendices']
analysis = db['analysis']
meta = db['meta']

all_collections = [regtext, interps, toc, appendices, meta]

json_root = '/Users/vinokurovy/Development/eregs-mongo/json'


def xml_to_json(root, counter, id_prefix, depth=1):
    """
    :param root: the root of the lxml.etree tree
    :param counter: the left/right node counter
    :param id_prefix: the version string used to generate the id
    :return: a jsonified version of the tree with left/right properties for nested set storage
    """
    json_node = OrderedDict()
    json_node['tag'] = root.tag.replace('{eregs}', '')
    if root.get('label') is not None:
        json_node['node_id'] = ':'.join([id_prefix, root.get('label')])
    elif json_node['tag'] in ['tableOfContents', 'fdsys', 'preamble']:
        json_node['node_id'] = ':'.join([id_prefix, json_node['tag']])

    json_node['attributes'] = dict(root.attrib)
    json_node['left'] = counter
    json_node['right'] = 0
    json_node['children'] = []
    json_node['depth'] = depth

    if root.text is not None and root.text.strip() != '':
        json_node['children'].append(root.text)

    counter += 1
    for child in root.getchildren():
        json_child, counter = xml_to_json(child, counter + 1, id_prefix, depth + 1)
        json_node['children'].append(json_child)
        if child.tail is not None and child.tail.strip() != '':
            json_node['children'].append(child.tail)
        counter += 1

    json_node['right'] = counter

    return json_node, counter


def recursive_insert(node):

    # delete anything with this node's node_id
    if 'node_id' in node:
        for coll in all_collections:
            coll.delete_many({'node_id': node['node_id']})

    # make a shallow copy of the node sans children
    node_to_insert = {}
    for key, value in node.items():
        if key != 'children':
            node_to_insert[key] = value

    # if we're a content node, we'd better restore the children that
    # we don't need to recurse on

    if node['tag'] in ['paragraph', 'interpParagraph', 'analysisParagraph']:
        for child in node['children']:
            if 'label' not in child['attributes']:
                node_to_insert.setdefault('children', []).append(child)

    # allow children for preamble and fdsys
    if node['tag'] in ['fdsys', 'preamble', 'tableOfContents']:
        node_to_insert['children'] = node['children']

    if node['tag'] in ['paragraph', 'section', 'appendix', 'appendixSection']:
        coll = regtext
    #elif node['tag'] in ['appendix', 'appendixSection']:
    #    coll = appendices
    elif node['tag'] in ['interpretations', 'interpParagraph', 'interpSection']:
        coll = interps
    elif node['tag'] in ['analysisSection', 'analysisParagraph']:
        coll = analysis
    elif node['tag'] in ['tableOfContents']:
        coll = toc
    elif node['tag'] in ['fdsys', 'preamble']:
        coll = meta
    else:
        raise ValueError('Unknown node encountered!')

    coll.insert_one(node_to_insert)

    # recurse only if this node has subchildren that are labeled
    # this ensures that paragraphs are the lowest level of recursion
    for child in node['children']:
        if 'label' in child['attributes']:
            recursive_insert(child)


def get_with_descendants(coll, node_id, return_format='nested'):
    """
    Fetch a node and all of its descendants. Depending on what you need, you can get the
    descendants in flat order as children of the initial result node, or you can get them
    in a nested format so that the nodes are nested by depth.
    :param coll: the collection from which to fetch
    :param node_id: the node_id of the node to retrieve
    :param return_format: either 'nested' or 'flat', defaults to 'nested'
    :return: the result, plus descendants in either nested or flat format
    """

    result = coll.find_one({'node_id': node_id})
    # dump the Mongo id, which is not serializable
    del result['_id']
    if result is None:
        return None

    node_prefix = ':'.join(node_id.split(':')[0:2])

    # NOTE: you HAVE TO match by node_id here because each version of the reg computes
    # its own hierarchy and therefore its own left/right values. If you don't filter
    # by node_id, you'll get garbage because the wrong versions will be picked up

    # TODO: change regex to a plain match once I get to internet access
    descendants = coll.find({'node_id': {'$regex': node_prefix},
                             'left': {'$gt': result['left']},
                             'right': {'$lt': result['right']}}, sort=[('left', ASCENDING)])
    result['children'] = []

    if return_format == 'nested':
        last_node_at_depth = {result['depth']: result}
        for desc in descendants:
            del desc['_id']
            last_node_at_depth[desc['depth']] = desc
            ancestor = last_node_at_depth[desc['depth'] - 1]
            ancestor.setdefault('children', []).append(desc)

    elif return_format == 'flat':
        for desc in descendants:
            del desc['_id']
            result['children'].append(desc)

    else:
        raise ValueError('Unknown return method!')

    return result


def get_ancestors(coll, node_id, ancestor_tag=None):
    """
    Retrieve all ancestors of a specific node. If the ancestor_tag is supplied, retrieve only
    those nodes that match the tag.
    :param coll: the collection to get from
    :param node_id: the node_id as a string
    :param ancestor_tag: the optional tag that the ancestor must have
    :return: a flat list of nodes representing the ancestors of the given node
    """

    # TODO: add the option to return as hierarchy, same as get_all_descendants
    
    node = coll.find_one({'node_id': node_id})
    # dump the Mongo id, which is not serializable
    del node['_id']
    if node is None:
        return None

    node_prefix = ':'.join(node_id.split(':')[0:2])

    query = {'node_id': {'$regex': node_prefix},
             'left': {'$lt': node['left']},
             'right': {'$gt': node['right']}}
    if ancestor_tag is not None:
        query['tag'] = ancestor_tag

    ancestors = coll.find(query)

    result = []
    for anc in ancestors:
        del anc['_id']
        result.append(anc)

    return result


def find_nodes(root, predicate, accum):
    """
    Find all nodes in a JSON tree that match a predicate.
    :param root: the root of the tree
    :param predicate: a boolean function
    :return: the node and all of its descendants
    """

    if predicate(root):
        accum.append(root)

    if isinstance(root, dict) and 'children' in root:
        for child in root['children']:
            find_nodes(child, predicate, accum)


def load_xml(xml_filename):

    with open(xml_filename, 'r') as f:
        xml = f.read()
        xml_tree = etree.fromstring(xml)

    preamble = xml_tree.find('.//{eregs}preamble')
    fdsys = xml_tree.find('.//{eregs}fdsys')
    doc_number = preamble.find('{eregs}documentNumber').text
    eff_date = preamble.find('{eregs}effectiveDate').text
    prefix = ':'.join([doc_number, eff_date])

    part = xml_tree.find('.//{eregs}part')
    part_content = part.find('{eregs}content')

    # clear out the subpart ToCs
    subparts = part_content.findall('{eregs}subpart')
    for subpart in subparts:
        subpart_toc = subpart.find('{eregs}tableOfContents')
        subpart.remove(subpart_toc)

    part_toc = part.find('{eregs}tableOfContents')

    # NOTE: it is IMPERATIVE that the JSONification occur starting
    # from the part (which is the root container of the reg).
    # This is because the process of transforming the XML to JSON
    # also sets the left and right attributes of the JSON nodes,
    # as well as the depth, which are used in the "nested sets"
    # formalism to easily select node descendants with a single
    # query. If you don't do this, you will end up with a situation
    # in which the order of nodes in the collection is lost and your
    # queries return garbage.

    part_content_tree, _ = xml_to_json(part_content, 1, prefix)
    part_toc_tree, _ = xml_to_json(part_toc, 1, prefix)

    # output_file = os.path.join(json_root, prefix + ':part.json')
    # json.dump(part_content_tree, open(output_file, 'w'), indent=4)

    # insert the metadata
    recursive_insert(xml_to_json(preamble, 1, prefix)[0])
    recursive_insert(xml_to_json(fdsys, 1, prefix)[0])

    # insert the sections

    sections = []

    def is_section(node):
        if isinstance(node, dict):
            return node['tag'] == 'section'
        else:
            return False

    def is_appendix(node):
        if isinstance(node, dict):
            return node['tag'] == 'appendix'
        else:
            return False

    find_nodes(part_content_tree, is_section, sections)
    for section in sections:
        recursive_insert(section)

    # insert the appendices

    appendixes = []
    find_nodes(part_content_tree, is_appendix, appendixes)
    for appendix in appendixes:
        recursive_insert(appendix)

    # insert the interps
    interpretations = part_content.find('{eregs}interpretations')
    interp_json, _ = xml_to_json(interpretations, 1, prefix)
    recursive_insert(interp_json)

    # insert the toc
    recursive_insert(part_toc_tree)

if __name__ == '__main__':

    xml_file = sys.argv[1]
    load_xml(xml_file)