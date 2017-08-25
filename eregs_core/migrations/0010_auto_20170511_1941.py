# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

# this migration manually runs the raw SQL to create the indices because the
# functions that do it pythonically are not available until Django 1.11 and
# we're still on Django 1.8


class Migration(migrations.Migration):
    dependencies = [
        ('eregs_core', '0009_auto_20170510_2021'),
    ]

    operations = [
        migrations.RunSQL(
            sql='''BEGIN;
--
-- Create index eregs_core__version_idx on field(s)
-- version, left_version, right_version of model version
--
CREATE INDEX `eregs_core__version_idx` ON `eregs_core_version` (
    `version`, `left_version`, `right_version`
);
--
-- Create index eregs_core__node_id_idx on field(s) node_id of model regnode
--
CREATE INDEX `eregs_core__node_id_idx` ON `eregs_core_regnode` (`node_id`);
--
-- Create index eregs_core__label_idx on field(s) label of model regnode
--
CREATE INDEX `eregs_core__label_idx` ON `eregs_core_regnode` (`label`);
--
-- Create index eregs_core__tag_idx on field(s) tag of model regnode
--
CREATE INDEX `eregs_core__tag_idx` ON `eregs_core_regnode` (`tag`);
--
-- Create index eregs_core__left_idx on field(s) left of model regnode
--
CREATE INDEX `eregs_core__left_idx` ON `eregs_core_regnode` (`left`);
--
-- Create index eregs_core__right_idx on field(s) right of model regnode
--
CREATE INDEX `eregs_core__right_idx` ON `eregs_core_regnode` (`right`);
COMMIT;''',
            reverse_sql='''BEGIN;
DROP INDEX eregs_core__version_idx ON eregs_core_version;
DROP INDEX eregs_core__node_id_idx ON eregs_core_regnode;
DROP INDEX eregs_core__label_idx ON eregs_core_regnode;
DROP INDEX eregs_core__tag_idx ON eregs_core_regnode;
DROP INDEX eregs_core__left_idx ON eregs_core_regnode;
DROP INDEX eregs_core__right_idx ON eregs_core_regnode;
COMMIT;'''
        )
    ]
