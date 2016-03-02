from django import template

register = template.Library()


def find_tag(root, tag):
    for child in [c for c in root['children'] if isinstance(c, dict)]:
        if child['tag'] == tag:
            return child
        elif isinstance(child, dict):
            find_tag(child, root)

@register.filter
def cfr_title_num(fdsys):
    child = find_tag(fdsys, 'cfrTitleNum')
    return child['children'][0]


@register.filter
def cfr_title_text(fdsys):
    child = find_tag(fdsys, 'cfrTitleText')
    return child['children'][0]

@register.filter
def cfr_section(preamble):
    cfr = find_tag(preamble, 'cfr')
    section = find_tag(cfr, 'section')
    return section['children'][0]

@register.filter
def cfr_title(preamble):
    cfr = find_tag(preamble, 'cfr')
    title = find_tag(cfr, 'title')
    return title['children'][0]

@register.filter
def reg_letter(preamble):
    letter = find_tag(preamble, 'regLetter')
    if letter is not None:
        return letter['children'][0]
    else:
        return ''

@register.filter
def doc_number(preamble):
    doc_num = find_tag(preamble, 'documentNumber')
    return doc_num['children'][0]

@register.filter
def effective_date(preamble):
    eff_date = find_tag(preamble, 'effectiveDate')
    return eff_date['children'][0]

@register.simple_tag
def reg_url(preamble):

    version_and_eff_date = preamble['node_id'].split(':')[0:2]
    section = cfr_section(preamble)
    link = '/'.join(['regulation'] + version_and_eff_date + [section + '-1'])
    return link