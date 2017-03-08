import json
import os

from collections import OrderedDict
from lxml import etree

json_root = '/Users/vinokurovy/Development/eregs-2.0/json'


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
    json_node['version'] = id_prefix

    if root.text is not None and root.text.strip() != '':
        counter += 1
        text_node = {'tag': 'regtext',
                     'content': root.text,
                     'left': counter,
                     'right': counter + 1,
                     'depth': depth + 1,
                     'children': [],
                     'version': id_prefix,
                     'node_type': 'reg',
                     'attributes': {}}
        counter += 1
        json_node['children'].append(text_node)


    #counter += 1
    for child in root.getchildren():
        json_child, counter = xml_to_json(child, counter + 1, id_prefix, depth + 1)
        json_node['children'].append(json_child)
        if child.tail is not None and child.tail.strip() != '':
            counter += 1
            text_node = {'tag': 'regtext',
                         'content': child.tail,
                         'left': counter,
                         'right': counter + 1,
                         'depth': depth + 1,
                         'children': [],
                         'version': id_prefix,
                         'node_type': 'reg',
                         'attributes': {}}
            json_node['children'].append(text_node)
            counter += 1
        counter += 1

    json_node['right'] = counter

    return json_node, counter


def xml_diff_to_json(root, counter, left_version, right_version, depth=1):
    """
    :param root: the root of the lxml.etree tree
    :param counter: the left/right node counter
    :param id_prefix: the version string used to generate the id
    :return: a jsonified version of the tree with left/right properties for nested set storage
    """
    json_node = OrderedDict()
    json_node['tag'] = root.tag.replace('{eregs}', '')
    if root.get('label') is not None:
        json_node['node_id'] = ':'.join([left_version, right_version, root.get('label')])
    elif json_node['tag'] in ['tableOfContents', 'fdsys', 'preamble']:
        json_node['node_id'] = ':'.join([left_version, right_version, json_node['tag']])

    json_node['attributes'] = dict(root.attrib)
    json_node['left'] = counter
    json_node['right'] = 0
    json_node['children'] = []
    json_node['depth'] = depth
    json_node['left_version'] = left_version
    json_node['right_version'] = right_version

    if root.text is not None and root.text.strip() != '':
        counter += 1
        text_node = {'tag': 'regtext',
                     'content': root.text,
                     'left': counter,
                     'right': counter + 1,
                     'depth': depth + 1,
                     'children': [],
                     'left_version': left_version,
                     'right_version': right_version,
                     'node_type': 'diff',
                     'attributes': {}}
        counter += 1
        json_node['children'].append(text_node)


    #counter += 1
    for child in root.getchildren():
        json_child, counter = xml_diff_to_json(child, counter + 1, left_version, right_version, depth + 1)
        json_node['children'].append(json_child)
        if child.tail is not None and child.tail.strip() != '':
            counter += 1
            text_node = {'tag': 'regtext',
                         'content': child.tail,
                         'left': counter,
                         'right': counter + 1,
                         'depth': depth + 1,
                         'children': [],
                         'left_version': left_version,
                         'right_version': right_version,
                         'node_type': 'diff',
                         'attributes': {}}
            json_node['children'].append(text_node)
            counter += 1
        counter += 1

    json_node['right'] = counter

    return json_node, counter




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


def extract_version(xml_tree):

    preamble = xml_tree.find('.//{eregs}preamble')
    doc_number = preamble.find('{eregs}documentNumber').text
    eff_date = preamble.find('{eregs}effectiveDate').text
    version = ':'.join([doc_number, eff_date])
    return version


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

    output_file = os.path.join(json_root, prefix + ':part.json')
    json.dump(part_content_tree, open(output_file, 'w'), indent=4)
    output_file = os.path.join(json_root, prefix + ':toc.json')
    json.dump(part_toc_tree, open(output_file, 'w'), indent=4)

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


def xml_node_text(node, include_children=True):
    """
    Extract the raw text from an XML element.

    :param node: the XML element, usually ``<content>``.
    :type node: :class:`etree.Element`
    :param include_children: whether or not to get the text of the children as well.
    :type include_children: :class:`bool` - optional, default = True

    :return: a string of the text of the node without any markup.
    :rtype: :class:`str`
    """

    if node.text:
        node_text = node.text
    else:
        node_text = ''

    if include_children:
        for child in node.getchildren():
            if child.text:
                node_text += child.text
            if child.tail:
                node_text += child.tail

    else:
        for child in node.getchildren():
            if child.tail:
                node_text += child.tail.strip()

    return node_text