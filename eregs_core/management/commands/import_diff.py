from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from eregs_core.models import DiffNode, Version
from eregs_core.utils import xml_diff_to_json
from eregs_core.diffs import diff_files
from lxml import etree

import os
import json
import time

from eregs.local_settings import DEBUG


class Command(BaseCommand):

    help = 'Import the diff between two RegML files into the database. The diff can be given as a single file ' \
           'that contains a precomputed diff, or as two regulation files from which the diff is computed.'

    def add_arguments(self, parser):
        parser.add_argument('version1', nargs='?')
        parser.add_argument('version2', nargs='?', default=None)

    def handle(self, *args, **options):

        version1 = options.get('version1')
        version2 = options.get('version2', None)

        if version1 is not None and version2 is not None:
            # we're given two files to diff, so compute the diff on the fly
            xml_tree, left_version, right_version = diff_files(options['version1'], options['version2'])
        elif version1 is not None and version2 is None:
            # only a single file given, so we assume it contains the diffs
            with open(version1, 'r') as f:
                xml_tree = etree.fromstring(f.read())
                split_version = os.path.split(version1)[-1].replace('.xml', '').split(':')
                if len(split_version) != 4:
                    print('File named incorrectly! Cannot infer versions!\n Make sure that your file ' \
                          'is named <left_doc_number>:<left_effective_date>:<right_doc_number>:<right_effective_date>')
                    exit(0)
                left_version = ':'.join(split_version[0:2])
                right_version = ':'.join(split_version[2:])
        else:
            print('Must supply at least one file that contains the diffs!')
            exit(0)

        part = xml_tree.find('.//{eregs}part')
        part_content = part.find('{eregs}content')

        # clear out the subpart ToCs
        subparts = part_content.findall('{eregs}subpart')
        for subpart in subparts:
            subpart_toc = subpart.find('{eregs}tableOfContents')
            subpart.remove(subpart_toc)

        # strip interp ToC to avoid duplicate ToC nodes
        interps = part_content.find('{eregs}interpretations')
        interp_toc = interps.find('{eregs}tableOfContents')
        interps.remove(interp_toc)

        # part_toc = part.find('{eregs}tableOfContents')

        # flush the table of existing content for this reg
        if DEBUG:
            start_time = time.clock()

        try:
            version = Version.objects.get(left_version=left_version, right_version=right_version)
            regulation = DiffNode.objects.filter(left_version=version.left_version,
                                                 right_version=version.right_version)
            regulation.delete()
            version.delete()

        except ObjectDoesNotExist:
            pass

        new_version = Version(left_version=left_version, right_version=right_version)
        new_version.save()

        reg_json = xml_diff_to_json(xml_tree, 1, left_version, right_version)[0]

        recursive_insert(reg_json, new_version)

        if DEBUG:
            end_time = time.clock()
            print('Import time for diff between {} and {} was {} seconds'.format(left_version, right_version,
                end_time - start_time))


def recursive_insert(node, version):

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

    new_node = DiffNode()
    new_node.tag = node['tag']
    new_node.node_id = node.get('node_id', '')
    new_node.label = node['attributes'].get('label', '')
    new_node.marker = node['attributes'].get('marker', '')
    new_node.attribs = node['attributes']
    new_node.right = node['right']
    new_node.left = node['left']
    new_node.depth = node['depth']
    new_node.reg_version = version
    #new_node.left_version = node['left_version']
    #new_node.right_version = node['right_version']
    if node['tag'] == 'regtext':
        new_node.text = node['content']

    new_node.save()

    # recurse only if this node has subchildren that are labeled
    # this ensures that paragraphs are the lowest level of recursion
    for child in node['children']:
        if type(child) is not str:
            recursive_insert(child, version)

