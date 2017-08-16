import os
import glob

from django.core.management import call_command
from django.core.management.base import BaseCommand
from eregs import local_settings

import time


class Command(BaseCommand):

    help = 'Import the specified regulation into the database.'

    def add_arguments(self, parser):

        parser.add_argument('part_number', nargs='?')

    def handle(self, *args, **options):

        part_number = options['part_number']
        if part_number is None:
            print 'Must supply a part number!'
            exit(0)

        reg_path = os.path.join(local_settings.REGML_ROOT, 'regulation', part_number)
        files = glob.glob(reg_path + '/*.xml')

        print 'RegML root in {}'.format(local_settings.REGML_ROOT)
        print 'Importing the regulation texts for {}'.format(part_number)
        start_time = time.clock()
        for filename in files:
            doc = os.path.split(filename)[1]
            print 'Importing {}'.format(doc)
            call_command('import_xml', filename)

        diff_path = os.path.join(local_settings.REGML_ROOT, 'diff', part_number)
        print 'Importing diffs between every pair of notices in {}'.format(part_number)
        files = glob.glob(diff_path + '/*.xml')

        for diff_file in files:
            split_version = os.path.split(diff_file)[-1].replace('.xml', '').split(':')
            if len(split_version) != 4:
                print('File named incorrectly! Cannot infer versions!\n Make sure that your file ' \
                      'is named <left_doc_number>:<left_effective_date>:<right_doc_number>:<right_effective_date>')
                exit(0)
            left_version = ':'.join(split_version[0:2])
            right_version = ':'.join(split_version[2:])
            print 'Importing diff between {} and {}'.format(left_version, right_version)
            call_command('import_diff', diff_file)
        end_time = time.clock()
        print 'Import took {} seconds'.format(end_time - start_time)
