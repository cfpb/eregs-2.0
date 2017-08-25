from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from eregs_core.models import RegNode, Version
from eregs_core.utils import xml_to_json
from lxml import etree

import os
import json


class Command(BaseCommand):

    help = 'Import the specified RegML file into the database.'

    def add_arguments(self, parser):
        parser.add_argument('regml_file', nargs='?')
        parser.add_argument('mode', nargs='?', default='reg')

    def handle(self, *args, **options):
        xml_filename = options['regml_file']
        with open(xml_filename, 'r') as f:
            xml = f.read()
            parser = etree.XMLParser(huge_tree=True)
            try:
                xml_tree = etree.fromstring(xml, parser)
            except etree.XMLSyntaxError as e:
                raise CommandError('There was a problem parsing {}!'.format(xml_filename))

        comments = xml_tree.xpath('//comment()')
        for comment in comments:
            parent = comment.getparent()
            parent.remove(comment)

        preamble = xml_tree.find('.//{eregs}preamble')
        fdsys = xml_tree.find('.//{eregs}fdsys')
        doc_number = preamble.find('{eregs}documentNumber').text
        if '_' in doc_number:
            doc_number = doc_number.split('_')[0]
        eff_date = preamble.find('{eregs}effectiveDate').text
        prefix = ':'.join([doc_number, eff_date])

        part = xml_tree.find('.//{eregs}part')
        part_content = part.find('{eregs}content')

        # clear out the subpart ToCs
        subparts = part_content.findall('{eregs}subpart')
        for subpart in subparts:
            subpart_toc = subpart.find('{eregs}tableOfContents')
            if subpart_toc is not None:
                subpart.remove(subpart_toc)

        # strip interp ToC to avoid duplicate ToC nodes
        interps = part_content.findall('{eregs}interpretations')
        for interp in interps:
            interp_toc = interp.find('{eregs}tableOfContents')
            if interp_toc is not None:
                interp.remove(interp_toc)

        # strip out the appendix ToCs also
        appendices = part_content.findall('{eregs}appendix')
        for appendix in appendices:
            appendix_toc = appendix.find('{eregs}tableOfContents')
            if appendix_toc is not None:
                appendix.remove(appendix_toc)

        # part_toc = part.find('{eregs}tableOfContents')

        # flush the table of existing content for this reg
        try:
            version = Version.objects.get(version=prefix)
            regulation = RegNode.objects.filter(reg_version=version)
            regulation.delete()
            version.delete()
        except ObjectDoesNotExist:
            pass

        new_version = Version(version=prefix)
        new_version.save()
        reg_json = xml_to_json(xml_tree, 1, prefix)[0]

        insert_all(reg_json, new_version)


def insert_all(node, version):

    result_nodes = []

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

        new_node = RegNode()
        new_node.tag = node['tag']
        new_node.node_id = node.get('node_id', '')
        new_node.label = node['attributes'].get('label', '')
        new_node.marker = node['attributes'].get('marker', '')
        new_node.attribs = node['attributes']
        new_node.right = node['right']
        new_node.left = node['left']
        new_node.depth = node['depth']
        new_node.reg_version = version

        if node['tag'] == 'regtext':
            new_node.text = node['content']

        result_nodes.append(new_node)
        #new_node.save()

        # recurse only if this node has subchildren that are labeled
        # this ensures that paragraphs are the lowest level of recursion
        for child in node['children']:
            if type(child) is not str:
                recursive_insert(child, version)

    recursive_insert(node, version)
    RegNode.objects.bulk_create(result_nodes, batch_size=100)
