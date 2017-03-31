# -*- coding: utf-8 -*-
import re
import json
import difflib

from hashlib import sha256
from utils import xml_node_text
from diffs import merge_text_diff
from django.db import models
from django.contrib.postgres.fields import JSONField

from itertools import product


class GenericNodeMixin(object):

    # this mixin class provides an interface for retrieving the descendants
    # of a node

    def __init__(self, *args, **kwargs):
        super(GenericNodeMixin, self).__init__(*args, **kwargs)
        self.children = []
        self.interps = []
        self.analysis = []

    def get_children(self, path):
        """
        Return all children matching the specified slash-separated path
        :param tag:
        :param get_all:
        :return:
        """
        elements = []

        def recursive_get_children(path):
            path = path.split('/')
            for i, elem in enumerate(path):
                for child in self.children:
                    if child.tag == elem:
                        if i < len(path) - 1:
                            recursive_get_children('/'.join(path[i + 1:]))
                        else:
                            elements.append(child)

        recursive_get_children(path)

        return elements

    def get_child(self, path):
        """
        Get a single child node specified by a slash-separated path between tags.
        Returns the first such node encountered.
        :param path:
        :return:
        """
        path = path.split('/')
        for i, elem in enumerate(path):
            for child in self.children:
                if child.tag == elem:
                    if i < len(path) - 1:
                        return child.get_child('/'.join(path[i + 1:]))
                    else:
                        return child

        return None

    def get_subnode_by_tag(self, tag):
        """
        Retrieve a single subnode by specified tag
        :param tag:
        :return:
        """
        for child in self.children:
            if child.tag == tag:
                return child

        return None

    def get_subnodes_by_tag(self, tag):
        """
        Get all subnodes by specified tag
        :return:
        """

        return [child for child in self.children if child.tag == tag]

    def node_text(self):
        text = ''
        for child in self.children:
            if child.get_child('regtext') is not None:
                text += child.get_child('regtext').text
            elif child.tag == 'regtext':
                text += child.text
        return text

    def get_descendants(self, desc_type=None, auto_infer_class=True, return_format='nested'):

        # Sometimes we'll want to instantiate nodes other than RegNodes. However,
        # only the caller knows which type of node it wants, and you can't reference
        # the class in the arguments until it's defined. So instead, we check if
        # desc_type is other than None; if it is, we use that class to pull
        # objects from the db, otherwise default to RegNode.

        if desc_type is None:
            desc_type = RegNode

        # print self.version, self.left, self.right

        if isinstance(self, DiffNode):
            descendants = desc_type.objects.filter(left_version=self.left_version,
                                                   right_version=self.right_version,
                                                   left__gt=self.left,
                                                   right__lt=self.right).order_by('left')
        elif isinstance(self, RegNode):
            descendants = desc_type.objects.filter(version__startswith=self.version,
                                                   left__gt=self.left,
                                                   right__lt=self.right).order_by('left')


        if return_format == 'nested':
            last_node_at_depth = {self.depth: self}
            for desc in descendants:
                if (desc_type is RegNode or desc_type is DiffNode) \
                        and auto_infer_class and desc.tag in tag_to_object_mapping:
                    desc.__class__ = tag_to_object_mapping[desc.tag]
                # print desc, desc.attribs, desc.depth
                # print desc, desc.depth
                last_node_at_depth[desc.depth] = desc
                ancestor = last_node_at_depth[desc.depth - 1]
                ancestor.children.append(desc)

    def get_ancestors(self, auto_infer_class=True):

        if isinstance(self, DiffNode):
            ancestors = DiffNode.objects.filter(left_version=self.left_version,
                                                right_version=self.right_version,
                                                left__lte=self.left,
                                                right__gte=self.right).order_by('left')
        elif isinstance(self, RegNode):
            ancestors = RegNode.objects.filter(left__lte=self.left,
                                               right__gte=self.right,
                                               version=self.version).order_by('left')
        else:
            ancestors = []

        if auto_infer_class:
            for ancestor in ancestors:
                if ancestor.tag in tag_to_object_mapping:
                    ancestor.__class__ = tag_to_object_mapping[ancestor.tag]

        return ancestors


class RegNode(models.Model, GenericNodeMixin):

    text = models.TextField()
    title = models.TextField()
    node_id = models.CharField(max_length=250)
    label = models.CharField(max_length=250)
    node_type = models.CharField(max_length=100)
    marker = models.CharField(max_length=25)
    tag = models.CharField(max_length=100)
    attribs = JSONField()
    version = models.CharField(max_length=250)

    left = models.IntegerField()
    right = models.IntegerField()
    depth = models.IntegerField()

    def __init__(self, *args, **kwargs):
        super(RegNode, self).__init__(*args, **kwargs)
        self.merkle_hash = ''

    # def __getitem__(self, item):
    #     """
    #     Implements getting the subnodes of a tree by using node tags as keys.
    #     :param item: the key
    #     :return: a list of all children that match the supplied tag
    #     """
    #     elements = []
    #     print item
    #     for child in self.children:
    #         if child.tag == item:
    #             elements.append(child)
    #     return elements


    def get_interpretations(self):

        interp_root = Paragraph.objects.filter(version=self.version, attribs__target=self.label, tag='interpParagraph')
        if len(interp_root) > 0:
            interp_root[0].get_descendants()
            self.interps = [interp_root[0]]

        return self.interps

    def get_analysis(self):

        analysis_root = AnalysisSection.objects.filter(version=self.version, tag='analysisSection', attribs__target=self.label)
        if len(analysis_root) > 0:
            analysis_root[0].get_descendants()
            self.analysis = [analysis_root[0]]

        return self.analysis

    def block_element_children(self):
        elements_with_children = ['section', 'paragraph', 'interpSection',
                                  'interpParagraph', 'interpretations', 'appendix', 'appendixSection']
        possible_children = ['paragraph', 'interpParagraph', 'section', 'interpSection', 'appendixSection']
        result = []

        if self.tag in elements_with_children:
            result = [child for child in self.children
                      if child.tag in possible_children]

        return result

    @property
    def marker_type(self):
        marker = self.marker.replace('(', '')
        marker = marker.replace(')', '')
        marker = marker.replace('.', '')
        return marker

    def inner_list_type(self):
        elements_with_inner_lists = ['section', 'interpSection', 'paragraph', 'interpParagraph', 'appendixSection']
        if self.tag in elements_with_inner_lists:
            first_par = self.get_child('paragraph')
            first_interp_par = self.get_child('interpParagraph')
            if first_par is not None and first_interp_par is None:
                marker = first_par.marker_type
            elif first_par is None and first_interp_par is not None:
                marker = first_interp_par.marker_type
            else:
                marker = 'none'

            return marker

    @property
    def is_paragraph(self):
        return self.tag in {'paragraph', 'interpParagraph'}

    def str_as_tree(self, depth=1):
        level_str = '-' * depth + self.tag + '\n'
        child_str = '\n'.join([child.str_as_tree(depth=depth+1) for child in self.children])
        return (level_str + child_str).replace('\n\n', '\n')

    def compute_merkle_hash(self):
        if self.children:
            child_hash = ''.join([child.merkle_hash() for child in self.children])
            if self.tag == 'regtext':
                self_hash = sha256(self.text.encode('utf-8') + child_hash).hexdigest()
            else:
                self_hash = sha256(self.tag + str(self.label) + json.dumps(self.attribs) + child_hash).hexdigest()
        else:
            if self.tag == 'regtext':
                self_hash = sha256(self.text.encode('utf-8')).hexdigest()
            else:
                self_hash = sha256(self.tag + str(self.label) + json.dumps(self.attribs)).hexdigest()

        self.merkle_hash = self_hash
        return self_hash

    def node_url(self):
        if self.tag == 'paragraph' or self.tag == 'interpParagraph':
            split_version = self.version.split(':')
            return '/regulation/{}/{}/{}'.format(split_version[0], split_version[1], self.label)

    def __str__(self):
        return '{}: {}'.format(self.tag, self.node_id)


class Preamble(RegNode):

    class Meta:
        proxy = True

    @property
    def agency(self):
        return self.get_child('agency/regtext').text

    @property
    def reg_letter(self):
        return self.get_child('regLetter/regtext').text

    @property
    def cfr_title(self):
        return self.get_child('cfr/title/regtext').text

    @property
    def cfr_section(self):
        return self.get_child('cfr/section/regtext').text

    @property
    def effective_date(self):
        return self.get_child('effectiveDate/regtext').text

    @property
    def document_number(self):
        return self.get_child('documentNumber/regtext').text

    @property
    def cfr_url(self):
        return self.get_child('federalRegisterURL/regtext').text

    @property
    def reg_url(self):
        version_and_eff_date = self.node_id.split(':')[0:2]
        section = self.cfr_section
        link = '/'.join(['regulation'] + version_and_eff_date + [section + '-1'])
        return link


class Fdsys(RegNode):

    class Meta:
        proxy = True

    @property
    def cfr_title(self):
        return self.get_child('cfrTitleNum/regtext').text

    @property
    def cfr_title_text(self):
        return self.get_child('cfrTitleText/regtext').text

    @property
    def volume(self):
        return self.get_child('volume/regtext').text

    @property
    def date(self):
        return self.get_child('date/regtext').text

    @property
    def original_date(self):
        return self.get_child('originalDate/regtext').text

    @property
    def part_title(self):
        return self.get_child('title/regtext').text

class TableOfContents(RegNode):

    class Meta:
        proxy = True

    @property
    def section_entries(self):
        return [entry for entry in self.children if entry.tag == 'tocSecEntry']

    @property
    def appendix_entries(self):
        return [entry for entry in self.children if entry.tag == 'tocAppEntry']

    @property
    def interp_entries(self):
        return [entry for entry in self.children if entry.tag == 'tocInterpEntry']

    @property
    def has_appendices(self):
        return len(self.appendix_entries) > 0

    @property
    def has_interps(self):
        return len(self.interp_entries) > 0

    @property
    def supplement_title(self):
        supplement = [entry for entry in self.children if entry.tag == 'tocInterpEntry' and
                        'Supplement' in entry.interp_title]
        print supplement
        if len(supplement) > 0:
            return supplement[0].interp_title

    @property
    def interp_intro_entry(self):
        intro_entry = [entry for entry in self.interp_entries if entry.interp_title == 'Introduction']
        if len(intro_entry) > 0:
            return intro_entry[0]

    @property
    def non_intro_interp_entries(self):
        if self.interp_intro_entry:
            return self.interp_entries[1:]


class ToCEntry(RegNode):

    class Meta:
        proxy = True

    def target(self):
        return self.attribs['target']

    @property
    def section_number(self):
        return self.get_child('sectionNum/regtext').text

    @property
    def section_subject(self):
        text = self.get_child('sectionSubject/regtext').text
        if self.tag == 'tocSecEntry':
            prefix = '§ {}'.format(self.target().replace('-', '.')).decode('utf-8')
            text = re.sub(prefix, '', text)
        return text

    @property
    def appendix_letter(self):
        if self.tag == 'tocAppEntry':
            return self.get_child('appendixLetter/regtext').text

    @property
    def appendix_subject(self):
        if self.tag == 'tocAppEntry':
            return self.get_child('appendixSubject/regtext').text

    @property
    def interp_title(self):
        if self.tag == 'tocInterpEntry':
            return self.get_child('interpTitle/regtext').text


class ToCSecEntry(RegNode):

    class Meta:
        proxy = True

    def target(self):
        return self.attribs['target']

    @property
    def section_number(self):
        return self.get_child('sectionNum/regtext').text

    @property
    def section_subject(self):
        text = self.get_child('sectionSubject/regtext').text
        if self.tag == 'tocSecEntry':
            prefix = '§ {}'.format(self.target().replace('-', '.')).decode('utf-8')
            text = re.sub(prefix, '', text)
        return text


class ToCAppEntry(RegNode):

    class Meta:
        proxy = True

    def target(self):
        return self.attribs['target']

    @property
    def appendix_letter(self):
        if self.tag == 'tocAppEntry':
            return self.get_child('appendixLetter/regtext').text

    @property
    def appendix_subject(self):
        if self.tag == 'tocAppEntry':
            return self.get_child('appendixSubject/regtext').text


class ToCInterpEntry(RegNode):

    class Meta:
        proxy = True

    def target(self):
        return self.attribs['target']

    @property
    def interp_title(self):
        if self.tag == 'tocInterpEntry':
            return self.get_child('interpTitle/regtext').text


class Section(RegNode):

    class Meta:
        proxy = True

    def section_number(self):
        if self.tag == 'section':
            return self.attribs['sectionNum']

    def appendix_letter(self):
        if self.tag == 'appendixSection':
            return self.attribs['appendixLetter']

    def label(self):
        return self.attribs['label']

    def get_all_analyses(self):
        if not self.children:
            self.get_descendants()

        analyses = []

        def collect_analyses(node):
            for child in node.children:
                if child.tag in {'paragraph', 'section', 'appedixSection'}:
                    analyses.extend(child.get_analysis())
                    collect_analyses(child)

        collect_analyses(self)
        self.analysis = analyses

        return analyses

    @property
    def subject(self):
        # print 'I am', self.label(), 'with title', self.get_child('subject/title')
        if self.tag == 'section' or self.tag == 'appendixSection':
            return self.get_child('subject/regtext').text
        elif self.tag == 'interpSection':
            title = self.get_child('title/regtext')
            if title:
                return title.text

    @property
    def paragraphs(self):
        return self.get_children('paragraph')

    @property
    def left_subject(self):
        l = None
        if self.tag == 'section' or self.tag == 'appendixSection':
            l = self.get_child('leftSubject/regtext')
        elif self.tag == 'interpSection':
            l = self.get_child('leftTitle/regtext')
        if l:
            return l.text
        else:
            return ''

    @property
    def right_subject(self):
        r = None
        if self.tag == 'section' or self.tag == 'appendixSection':
            r = self.get_child('rightSubject/regtext')
        elif self.tag == 'interpSection':
            r = self.get_child('rightTitle/regtext')
        if r:
            return r.text
        else:
            return ''

    def action(self):
        return self.attribs.get('action', None)

    @property
    def has_diff_subject(self):
        return self.left_subject != '' and self.right_subject != ''

    @property
    def subject_diff(self):
        print 'label', self.label
        if self.has_diff_subject:
            #print self.label, 'has diff title'
            left_text = self.left_subject
            right_text = self.right_subject
            diff = difflib.ndiff(left_text, right_text)
            #print 'left:', left_text, 'right:', right_text
            text = merge_text_diff(diff)
            print text
            return text


class Paragraph(RegNode):

    class Meta:
        proxy = True

    def target(self):
        return self.attribs.get('target', None)

    def interp_target(self):
        # for display purposes
        if 'target' in self.attribs:
            split_target = self.attribs['target'].split('-')
            section = split_target[1]
            interp_target = ''.join([section] + ['({})'.format(item) for item in split_target[2:]])
            return interp_target
        else:
            return None

    @property
    def has_content(self):
        return self.get_child('content') is not None

    @property
    def has_diff_content(self):
        return self.get_child('leftContent') is not None and self.get_child('rightContent') is not None

    @property
    def paragraph_content(self):
        content = self.get_child('content')
        return content.children

    @property
    def paragraph_title(self):
        return self.get_child('title/regtext').text

    @property
    def regtext(self):
        return self.get_child('regtext').text

    @property
    def left_content(self):
        lc = self.get_child('leftContent')
        if lc:
            return lc.children

    @property
    def right_content(self):
        rc = self.get_child('rightContent')
        if rc:
            return rc.children

    @property
    def left_title(self):
        l = self.get_child('leftTitle')
        if l:
            return l.get_child('regtext').text or ''

    @property
    def right_title(self):
        r = self.get_child('rightTitle')
        if r:
            return r.get_child('regtext').text or ''

    @property
    def has_diff_title(self):
        return self.get_child('leftTitle') is not None and self.get_child('rightTitle') is not None

    @property
    def content_diff(self):
        if self.has_diff_content:
            left_text = self.get_child('leftContent').node_text()
            right_text = self.get_child('rightContent').node_text()
            diff = difflib.ndiff(left_text, right_text)
            text = merge_text_diff(diff)
            return text

    @property
    def title_diff(self):
        if self.has_diff_title:
            print self.label, 'has diff title'
            left_text = self.left_title
            right_text = self.right_title
            diff = difflib.ndiff(left_text, right_text)
            print 'left:', left_text, 'right:', right_text
            text = merge_text_diff(diff)
            return text

    def action(self):
        return self.attribs.get('action', None)

    def marked_up_content(self):
        content = self.get_child('content')
        text = ''
        for child in content.children:
            if child.tag == 'regtext':
                text += child.text
            elif child.tag == 'def':
                text += '<dfn class="defined-term">{}</dfn>'.format(child.regtext())
            elif child.tag == 'ref':
                text += '<a href="{}" class="citation definition" data-definition="{}"' \
                        ' data-defined-term="{}" data-gtm-ignore-"true">{}</a>'.format(child.target_url(),
                                                                                       child.target(),
                                                                                       child.regtext(),
                                                                                       child.regtext())
        return text

    def formatted_label(self):
        label = self.label.split('-')
        return label[0] + '.' + label[1] + ''.join(['({})'.format(item) for item in label[2:]])


class Reference(RegNode):

    class Meta:
        proxy = True

    def reftype(self):
        return self.attribs['reftype']

    def target(self):
        return self.attribs['target']

    def regtext(self):
        return self.get_child('regtext').text

    def target_url(self):
        if self.reftype() == 'internal' or self.reftype() == 'term':
            split_version = self.version.split(':')
            split_target = self.target().split('-')
            target = None
            if 'Interp' in split_target:
                if len(split_target) == 2:
                    target = self.target()
                elif len(split_target) > 2:
                    target = split_target[0] + '-Interp#' + self.target()
            else:
                if len(split_target) == 2:
                    target = self.target()
                elif len(split_target) > 2:
                    target = split_target[0] + '-' + split_target[1] + '#' + self.target()
            try:
                url = '/regulation/{}/{}/{}'.format(split_version[0], split_version[1], target)
                return url
            except Exception:
                # we don't want to die if this happens, but we should definitely log the error
                print 'Invalid target {} at text {}! '.format(str(self.target()), self.regtext())
                return ''

        else:
            return self.target()


class Definition(RegNode):

    class Meta:
        proxy = True

    def term(self):
        return self.attribs['term']

    def regtext(self):
        return self.get_child('regtext').text


class Appendix(RegNode):

    class Meta:
        proxy = True

    def appendix_letter(self):
        return self.attribs['appendixLetter']

    def label(self):
        return self.attribs['label']

    @property
    def appendix_title(self):
        return self.get_child('appendixTitle/regtext')

    @property
    def regtext(self):
        return self.get_child('regtext').text


# class SectionBySectionNode(models.Model, GenericNodeMixin):
#
#     text = models.TextField()
#     tag = models.CharField(max_length=100)
#     attribs = JSONField()
#     version = models.CharField(max_length=250)
#
#     left = models.IntegerField()
#     right = models.IntegerField()
#     depth = models.IntegerField()


class AnalysisSection(RegNode):

    class Meta:
        proxy = True

    def target(self):
        return self.attribs['target']

    def notice(self):
        return self.attribs['notice']

    def effective_date(self):
        return self.attribs['date']

    def section_title(self):
        return self.get_child('title/regtext').text

    def analysis_target(self):
        split_target = self.attribs['target'].split('-')
        section = split_target[1]
        return ''.join([section] + ['({})'.format(item) for item in split_target[2:]])

    def target_url(self):
        return '/partial/sxs/{}/{}/{}'.format(self.version.split(':')[0], self.version.split(':')[1], self.target())


class AnalysisParagraph(RegNode):

    class Meta:
        proxy = True


class Footnote(RegNode):

    class Meta:
        proxy = True

    def ref(self):
        return self.attribs['ref']

    def footnote_text(self):
        return self.get_child('regtext').text


class DiffNode(RegNode):

    left_version = models.CharField(max_length=250)
    right_version = models.CharField(max_length=250)


class DiffPreamble(Preamble, RegNode):

    class Meta:
        proxy = True

    @property
    def left_document_number(self):
        return self.left_version.split(':')[0]

    @property
    def left_effective_date(self):
        return self.left_version.split(':')[1]

    @property
    def right_document_number(self):
        return self.right_version.split(':')[0]

    @property
    def right_effective_date(self):
        return self.right_version.split(':')[1]


# top-level because it needs to have all the classes defined
tag_to_object_mapping = {
    'paragraph': Paragraph,
    'interpParagraph': Paragraph,
    'appendixSection': Section,
    'interpSection': Section,
    'section': Section,
    'ref': Reference,
    'def': Definition,
    'tocSecEntry': ToCSecEntry,
    'tocAppEntry': ToCAppEntry,
    'tocInterpEntry': ToCInterpEntry,
    'analysisSection': AnalysisSection,
    'analysisParagraph': AnalysisParagraph,
    'footnote': Footnote
}