import os
import glob
import time

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Import the specified regulation into the database.'

    def add_arguments(self, parser):
        parser.add_argument('-r', '--regml-root', help='RegML root',
                            required=True)
        parser.add_argument('part_number', nargs='+')

    def handle(self, *args, **options):
        part_number = options['part_number']
        regml_root = options['regml_root']

        if not os.path.isdir(regml_root):
            raise CommandError('{} is not a directory'.format(regml_root))

        for part_number in options['part_number']:
            self.handle_part(regml_root, part_number)

    def handle_part(self, regml_root, part_number):
        reg_path = os.path.join(regml_root, 'regulation', part_number)
        files = glob.glob(reg_path + '/*.xml')

        if not files:
            raise ValueError('no files in {}'.format(reg_path))

        print 'RegML root in {}'.format(regml_root)
        print 'Importing the regulation texts for {}'.format(part_number)
        start_time = time.clock()
        for filename in files:
            doc = os.path.split(filename)[1]
            print 'Importing {}'.format(doc)
            call_command('import_xml', filename)

        diff_path = os.path.join(regml_root, 'diff', part_number)
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
