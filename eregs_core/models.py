from django.db import models
from mongoengine import *

# Create your models here.

connect('eregs')


class RegNode(Document):

    text = StringField()
    title = StringField()
    label = StringField()
    node_type = StringField()
    marker = StringField()

    children = ListField(ReferenceField('self'))

