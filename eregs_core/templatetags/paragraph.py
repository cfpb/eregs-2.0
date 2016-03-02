from django import template
from marker import marker_type

register = template.Library()


def find_tag(root, tag):
    for child in [c for c in root['children'] if isinstance(c, dict)]:
        if child['tag'] == tag:
            return child
        elif isinstance(child, dict):
            find_tag(child, root)

@register.filter
def paragraph_content(root):
    content = find_tag(root, 'content')
    return content['children']

@register.filter
def paragraph_title(root):
    return find_tag(root, 'title')

@register.simple_tag
def ref_url(ref, meta):
    version_and_eff_date = meta['node_id'].split(':')[0:2]
    target = ref['attributes']['target']
    if 'Interp' in target:
        link = '/'.join(['interpretations'] + version_and_eff_date + [target])
    else:
        link = '/'.join(['regulation'] + version_and_eff_date + [target])

    return '/' + link

@register.filter
def block_element_children(node):
    result = []
    elements_with_children = ['section', 'paragraph', 'interpSection',
                              'interpParagraph', 'interpretations', 'appendix']
    possible_children = ['paragraph', 'interpParagraph', 'section', 'interpSection']
    if node['tag'] in elements_with_children:
        result = [child for child in node['children']
                  if child['tag'] in possible_children]

    return result

@register.filter
def inner_list_type(node):
    elements_with_inner_lists = ['section', 'interpSection', 'paragraph', 'interpParagraph']
    if node['tag'] in elements_with_inner_lists:
        first_par = find_tag(node, 'paragraph')
        first_interp_par = find_tag(node, 'interpParagraph')
        if first_par is not None and first_interp_par is None:
            marker = marker_type(first_par['attributes'].get('marker', 'none'))
        elif first_par is None and first_interp_par is not None:
            marker = marker_type(first_interp_par['attributes'].get('marker', 'none'))
        else:
            marker = 'none'

        return marker