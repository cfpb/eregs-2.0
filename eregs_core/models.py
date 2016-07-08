from django.db import models
from django.contrib.postgres.fields import JSONField

from itertools import product

# class RegNode(Document):
#
#     text = StringField()
#     title = StringField()
#     label = StringField()
#     node_type = StringField()
#     marker = StringField()
#
#     children = ListField(ReferenceField('self'))
#


class RegNode(models.Model):

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
        self.children = []

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

    def get_descendants(self, desc_type=None, return_format='nested'):

        # Sometimes we'll want to instantiate nodes other than RegNodes. However,
        # only the caller knows which type of node it wants, and you can't reference
        # the class in the arguments until it's defined. So instead, we check if
        # desc_type is other than None; if it is, we use that class to pull
        # objects from the db, otherwise default to RegNode.

        if desc_type is None:
            desc_type = RegNode

        print self.version, self.left, self.right

        descendants = desc_type.objects.filter(version__startswith=self.version,
                                               left__gt=self.left,
                                               right__lt=self.right).order_by('left')

        if return_format == 'nested':
            last_node_at_depth = {self.depth: self}
            for desc in descendants:
                last_node_at_depth[desc.depth] = desc
                ancestor = last_node_at_depth[desc.depth - 1]
                ancestor.children.append(desc)

    def block_element_children(self):
        elements_with_children = ['section', 'paragraph', 'interpSection',
                                  'interpParagraph', 'interpretations', 'appendix']
        possible_children = ['paragraph', 'interpParagraph', 'section', 'interpSection']
        result = []

        # paths = product(elements_with_children, possible_children)

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
        elements_with_inner_lists = ['section', 'interpSection', 'paragraph', 'interpParagraph']
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

    def str_as_tree(self, depth=1):
        level_str = '-' * depth + self.tag + '\n'
        child_str = '\n'.join([child.str_as_tree(depth=depth+1) for child in self.children])
        return (level_str + child_str).replace('\n\n', '\n')


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


class TableOfContents(RegNode):

    class Meta:
        proxy = True


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
        return self.get_child('sectionSubject/regtext').text

    @property
    def appendix_letter(self):
        return self.get_child('appendixLetter/regtext').text

    @property
    def appendix_subject(self):
        return self.get_child('appendixSubject/regtext').text


class Section(RegNode):

    class Meta:
        proxy = True

    # for some reason I don't entirely understand yet having this as a property causes an attribute error

    def section_number(self):
        return self.attribs['sectionNum']

    # @property
    def label(self):
        return self.attribs['label']

    @property
    def subject(self):
        return self.get_child('subject/regtext').text

    @property
    def paragraphs(self):
        return self.get_children('paragraph')


class Paragraph(RegNode):

    class Meta:
        proxy = True

    def target(self):
        return self.attribs['target']

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

    def reftype(self):
        return self.attribs['reftype']