# -*- coding: utf-8 -*-
import sys, os, pprint
from os import path
import coverage
from optparse import make_option
from django.conf import settings
from django.core.management.base import BaseCommand
from django_hudson.management.commands.lint import Command as pylint
from django_hudson.xmlrunner import XmlDjangoTestSuiteRunner
from django_hudson.management.commands.xmltest import patch_for_test_db_setup

class Command(BaseCommand):
    help = "Run ci process"

    option_list = BaseCommand.option_list + (
        make_option('--output', dest='output_dir', default='reports',
                    help='Reports directory'),
        make_option('--noinput', action='store_false', dest='interactive', default=True,
            help='Tells Django to NOT prompt the user for input of any kind.'),
        make_option('--excludes', dest="excludes", default='',
            help="""Comma seperated list of words, modules containing those words
            will be excluded from coverage reports."""),
    )

    def handle(self, *test_labels, **options):
        """
        Run pylint and test with coverage and xml reports
        """
        patch_for_test_db_setup()

        verbosity = int(options.get('verbosity', 1))
        interactive = options.get('interactive', True)
        excludes = options.get('excludes', '').split(',')
        excludes = [ exclude.strip() for exclude in excludes ]
        
        output_dir=options.get('output_dir')
        if not path.exists(output_dir):
            os.makedirs(output_dir)

        if not test_labels:
            test_labels = Command.test_labels()

        #TODO: Make lint work and with external rc file
        # pylint
        #pylint().handle(*app_labels, 
                         #output_file=path.join(output_dir,'pylint.report'))

        #coverage
        coverage.exclude('#pragma[: ]+[nN][oO] [cC][oO][vV][eE][rR]')
        coverage.start()
        
        #tests
        test_runner = XmlDjangoTestSuiteRunner(output_dir=output_dir, interactive=interactive, verbosity=verbosity)
        failures = test_runner.run_tests(test_labels)

        #save coverage report
        coverage.stop()

        modules = [ (module, name) for name, module in sys.modules.items() \
                       if module and any([label for label in test_labels if label in name]) ]
        modules = [ module for module, name in modules if self.want_module(name, excludes) ]
        
        modules = [ module for module in modules if self.src(module.__file__).endswith('.py') ]

        if verbosity > 0:
            if excludes:
                print "Excluding any module containing of these words:"
                pprint.pprint(excludes)
            
            print "Coverage being generated for:"
            pprint.pprint(modules)

        morfs = [ m.__file__ for m in modules if hasattr(m, '__file__') ]
        coverage._the_coverage.xml_report(morfs, outfile=path.join(output_dir,'coverage.xml'))

    def want_module(self, filename, excludes=[]):
        for exclude in excludes:
            if exclude and exclude in filename:
                return False
        return True

    def src(self, filename):
        """Find the python source file for a .pyc, .pyo or $py.class file on
        jython. Returns the filename provided if it is not a python source
        file. Cribbed from nose.util
        """
        if filename is None:
            return filename
        if sys.platform.startswith('java') and filename.endswith('$py.class'):
            return '.'.join((filename[:-9], 'py'))
        base, ext = os.path.splitext(filename)
        if ext in ('.pyc', '.pyo', '.py'):
            return '.'.join((base, 'py'))
        return filename
    
    @staticmethod
    def test_labels():
        excludes = getattr(settings, 'TEST_EXCLUDES', [])
        return [app for app in settings.INSTALLED_APPS if app not in excludes ]