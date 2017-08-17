# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('eregs_core', '0011_tocsubpartentry'),
    ]

    operations = [
        migrations.DeleteModel(
            name='DiffNode',
        ),
        migrations.CreateModel(
            name='DiffNode',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('eregs_core.regnode',),
        ),
    ]
