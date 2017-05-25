from haystack import indexes
from models import RegNode


class RegNodeIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.CharField(document=True, use_template=True)
    version = indexes.CharField(model_attr='reg_version__version', null=True)

    def get_model(self):

        return RegNode

    def index_queryset(self, using=None):

        return self.get_model().objects.all()