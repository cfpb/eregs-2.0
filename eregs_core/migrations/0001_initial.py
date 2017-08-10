# -*- coding: utf-8 -*-
from __future__ import unicode_literals


from django.db import migrations, models

from eregs_core import LEGACY_JSON_LOOKUPS

# import django.contrib.postgres.fields.jsonb

if LEGACY_JSON_LOOKUPS:
    from jsonfield import JSONField
else:
    from django_mysql.models import JSONField


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RegNode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('title', models.TextField()),
                ('label', models.CharField(max_length=250)),
                ('node_type', models.CharField(max_length=100)),
                ('marker', models.CharField(max_length=25)),
                ('tag', models.CharField(max_length=100)),
                ('attribs', JSONField()),
                ('left', models.IntegerField()),
                ('right', models.IntegerField()),
                ('depth', models.IntegerField()),
            ],
        ),
    ]
