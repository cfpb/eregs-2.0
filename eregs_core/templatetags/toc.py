from django import template
from meta import cfr_section

register = template.Library()


def find_tag(root, tag):
    for child in [c for c in root['children'] if isinstance(c, dict)]:
        if child['tag'] == tag:
            return child
        elif isinstance(child, dict):
            find_tag(child, root)


@register.simple_tag
def entry_url(entry, meta):

    version_and_eff_date = meta['node_id'].split(':')[0:2]

    app_letter = find_tag(entry, 'appendixLetter')
    if app_letter is None:
        link = '/'.join(['regulation'] + version_and_eff_date + [entry['attributes']['target']])
    elif app_letter['children'][0] == 'Interp':
        link = '/'.join(['interpretations'] + version_and_eff_date + [entry['attributes']['target']])
    else:
        link = '/'.join(['regulation'] + version_and_eff_date + [entry['attributes']['target']])
    return '/' + link