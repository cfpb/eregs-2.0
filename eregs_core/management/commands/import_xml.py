from django.core.management.base import BaseCommand, CommandError
from eregs_core.models import RegNode
from eregs_core.utils import xml_to_json
from lxml import etree

import os
import json

json_root = '/Users/vinokurovy/Development/eregs-2.0/json'

class Command(BaseCommand):

    help = 'Import the specified RegML file into the database.'

    def add_arguments(self, parser):
        parser.add_argument('regml_file', nargs='?')

    def handle(self, *args, **options):
        xml_filename = options['regml_file']
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

        # part_toc = part.find('{eregs}tableOfContents')

        reg_json = xml_to_json(xml_tree, 1, prefix)[0]

        recursive_insert(reg_json)

        output_file = os.path.join(json_root, prefix + ':reg.json')
        json.dump(reg_json, open(output_file, 'w'), indent=4)

def recursive_insert(node):

    # delete anything with this node's node_id
    if 'node_id' in node:
        for reg_node in RegNode.objects.filter(node_id=node['node_id']):
            reg_node.delete()

    # make a shallow copy of the node sans children
    node_to_insert = {}
    for key, value in node.items():
        if key != 'children':
            node_to_insert[key] = value

    # if we're a content node, we'd better restore the children that
    # we don't need to recurse on

    if node['tag'] in ['paragraph', 'interpParagraph', 'analysisParagraph',
                       'section', 'appendix', 'tocSecEntry', 'tocAppEntry',
                       'interpSection', 'interpretations', 'tableOfContents']:
        for child in node['children']:
            if 'label' not in child['attributes']:
                node_to_insert.setdefault('children', []).append(child)

    # allow children for preamble and fdsys
    if node['tag'] in ['fdsys', 'preamble']:
        node_to_insert['children'] = node['children']

    new_node = RegNode()
    new_node.tag = node['tag']
    new_node.node_id = node.get('node_id', '')
    new_node.label = node['attributes'].get('label', '')
    new_node.marker = node['attributes'].get('marker', '')
    new_node.attribs = node['attributes']
    new_node.right = node['right']
    new_node.left = node['left']
    new_node.depth = node['depth']
    new_node.version = node['version']
    if node['tag'] == 'regtext':
        new_node.text = node['content']

    new_node.save()

    # recurse only if this node has subchildren that are labeled
    # this ensures that paragraphs are the lowest level of recursion
    for child in node['children']:
        if type(child) is not str:
            recursive_insert(child)

