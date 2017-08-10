from distutils.core import setup
from setuptools import find_packages


install_requires = (
    'Django>=1.8,<1.12',
    'django-extensions',
    'django-haystack',
    'jsonfield==2.0.2',
    'lxml',
    'python-dateutil',
    'sqlparse',
)


testing_extras = (
    'MySQL-python==1.2.5',
    'coverage>=3.7.0',
    'django-mysql==2.1.0',
    'model_mommy==1.2.6',
    'selenium==3.4.3',
)


setup(
    name='eregs',
    version='0.0.1',
    author='Jerry Vinokurov and Chris Contolini',
    author_email='yury.vinokurov@cfpb.gov',
    packages=find_packages(),
    url='https://github.com/cfpb/eregs-2.0',
    license='MIT',
    description='The new version of eRegs.',
    include_package_data=True,
    install_requires=install_requires,
    setup_requires=['cfgov_setup==1.2'],
    frontend_build_script='setup.sh',
    extras_require={
        'testing': testing_extras,
    },
)
