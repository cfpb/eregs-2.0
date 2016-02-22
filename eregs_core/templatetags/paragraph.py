from django import template

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