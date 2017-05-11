#!/usr/bin/env python

import json
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

# from eregs_core.models import RegNode

from utils import xml_node_text, extract_version
from lxml import etree
from copy import deepcopy

def load_xml(filename):
    with open(filename, 'r') as f:
        data = f.read()
        return etree.fromstring(data)


def gather_regnode_labels(root):

    labels = []

    def recursive_gather(node):
        if node.label is not None:
            labels.append(node.label)
        for child in node.children:
            recursive_gather(child)

    recursive_gather(root)

    return labels


def diff_trees(left_version, right_version):

    left_tree = RegNode.objects.get(tag='regulation', version=left_version)
    right_tree = RegNode.objects.get(tag='regulation', version=right_version)

    left_tree.get_descendants()
    right_tree.get_descendants()

    left_tree.compute_merkle_hash()
    right_tree.compute_merkle_hash()

    left_labels = set(gather_regnode_labels(left_tree))
    right_labels = set(gather_regnode_labels(right_tree))

    only_left_labels = left_labels - right_labels
    only_right_labels = right_labels - left_labels

    both_labels = left_labels & right_labels

    # only right labels were added
    for label in only_right_labels:
        pass


def gather_labels(tree):

    labels = []

    def recursive_gather(node):
        if node.get('label') is not None:
            labels.append(node.get('label'))
        for child in node:
            recursive_gather(child)

    recursive_gather(tree)

    return labels


def set_descendants_property(root, prop_name, prop_value):

    root.set(prop_name, prop_value)

    for child in root:
        set_descendants_property(child, prop_name, prop_value)


def diff_files(left_filename, right_filename, output_file='diff.xml'):

    left_tree = load_xml(left_filename)
    right_tree = load_xml(right_filename)

    left_labels = gather_labels(left_tree)
    right_labels = gather_labels(right_tree)

    only_left_labels = [label for label in left_labels if label not in right_labels]
    only_right_labels = [label for label in right_labels if label not in left_labels]

    common_labels = [label for label in left_labels if label in right_labels]

    # clear out any right-hand labels that aren't top-level
    top_level_right_labels = set()
    for label in only_right_labels:
        element = right_tree.find('.//*[@label="{}"]'.format(label))
        current_parent = element.getparent()
        last_label = element.get('label')
        while current_parent.get('label') in only_right_labels:
            last_label = current_parent.get('label')
            current_parent = current_parent.getparent()
        top_level_right_labels.add(last_label)

    for label in top_level_right_labels:
        element = right_tree.find('.//*[@label="{}"]'.format(label))
        common_ancestor, prev_sibling = left_tree_ancestor(left_tree, element)
        set_descendants_property(element, 'action', 'added')
        if prev_sibling is not None:
            prev_sibling.addnext(deepcopy(element))
        else:
            common_ancestor.append(deepcopy(element))

    for label in only_left_labels:
        element = left_tree.find('.//*[@label="{}"]'.format(label))
        set_descendants_property(element, 'action', 'deleted')

    for label in common_labels:
        left_element = left_tree.find('.//*[@label="{}"]'.format(label))
        right_element = right_tree.find('.//*[@label="{}"]'.format(label))
        assert (left_element.tag == right_element.tag)

        if left_element.tag == '{eregs}section':
            left_subject_el = left_element.find('{eregs}subject')
            right_subject_el = right_element.find('{eregs}subject')
            left_subject = left_subject_el.text.strip()
            right_subject = right_subject_el.text.strip()

            if left_subject != right_subject:
                left_subject_el.tag = '{eregs}leftSubject'
                right_subject_el.tag = '{eregs}rightSubject'
                left_subject_el.addnext(right_subject_el)
                left_element.attrib['action'] = 'modified'

        elif left_element.tag == '{eregs}interpSection':
            try:
                left_title_el = left_element.find('{eregs}title')
                left_title = left_title_el.text.strip()
            except AttributeError:
                left_title = ''
            try:
                right_title_el = right_element.find('{eregs}title')
                right_title = right_title_el.text.strip()
            except AttributeError:
                right_title = ''

            if left_title != right_title:
                if left_title_el is not None and right_title_el is not None:
                    left_title_el.tag = '{eregs}leftTitle'
                    right_title_el.tag = '{eregs}rightTitle'
                    left_title_el.addnext(deepcopy(right_title_el))
                    left_element.attrib['action'] = 'modified'

        elif left_element.tag == '{eregs}paragraph' or left_element.tag == '{eregs}interpParagraph':
            try:
                left_title_el = left_element.find('{eregs}title')
                left_title = left_title_el.text.strip()
            except AttributeError:
                left_title = ''
            try:
                right_title_el = left_element.find('{eregs}title')
                right_title = right_title_el.text.strip()
            except AttributeError:
                right_title = ''

            if left_title != right_title:
                if left_title_el is not None and right_title_el is not None:
                    left_title_el.tag = '{eregs}leftTitle'
                    right_title_el.tag = '{eregs}rightTitle'
                    left_title_el.addnext(deepcopy(right_title_el))
                    left_element.attrib['action'] = 'modified'

            left_content = left_element.find('{eregs}content')
            left_text = xml_node_text(left_content).strip()
            right_content = right_element.find('{eregs}content')
            right_text = xml_node_text(right_content).strip()
            if left_text != right_text:
                left_content.tag = '{eregs}leftContent'
                right_content.tag = '{eregs}rightContent'
                left_content.addnext(deepcopy(right_content))
                left_element.attrib['action'] = 'modified'

    return left_tree, extract_version(left_tree), extract_version(right_tree)


def left_tree_ancestor(left_tree, right_node):
    """
    :param left_tree: The left XML tree
    :param right_node: A node from the right tree that was added
    :return: The element from the left tree under which the right_node can be inserted
    and the element *after* which it is to be inserted
    """

    common_ancestor = None
    left_sibling = None
    stop = False
    current_right = right_node

    while not common_ancestor and not stop:
        right_node_parent = current_right.getparent()
        left_ancestor = left_tree.find('.//*[@label="{}"]'.format(right_node_parent.get('label')))

        if left_ancestor:
            stop = True
            common_ancestor = left_ancestor
        else:
            current_right = right_node_parent

    stop = False

    while not left_sibling and not stop:
        for child in common_ancestor:
            if child.get('label') == right_node.getprevious().get('label'):
                left_sibling = child
        stop = True

    return common_ancestor, left_sibling


def merge_text_diff(diff):

    text = ''
    flag = 'common' # other values: add, delete
    for d in diff:
        if d[0] == ' ':
            if flag == 'delete':
                text += '</del>' + d[2]
            elif flag == 'add':
                text += '</ins>' + d[2]
            elif flag == 'common':
                text += d[2]
            flag = 'common'
        elif d[0] == '-':
            if flag == 'common':
                text += '<del>' + d[2]
            elif flag == 'delete':
                text += d[2]
            elif flag == 'add':
                text += '</ins>' + '<del>' + d[2]
            flag = 'delete'
        elif d[0] == '+':
            if flag == 'common':
                text += '<ins>' + d[2]
            elif flag == 'add':
                text += d[2]
            elif flag == 'delete':
                text += '</del>' + '<ins>' + d[2]
            flag = 'add'

    if flag == 'add':
        text += '</ins>'
    elif flag == 'delete':
        text += '</del>'

    return text


if __name__ == '__main__':

    left_file = sys.argv[1]
    right_file = sys.argv[2]

    diff_files(left_file, right_file)