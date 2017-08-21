from distutils.core import setup


install_requires = (
    'Django>=1.8,<1.12',
    'django-extensions',
    'django-haystack',
    'jsonfield==2.0.2',
    'lxml',
    'python-dateutil',
    'sqlparse',
)


setup_requires = (
    'cfgov_setup==1.2',
    'setuptools-git-version==1.0.3',
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
    version_format='{tag}.dev{commitcount}+{gitsha}',
    author='CFPB',
    author_email='tech@cfpb.gov',
    packages=['eregs_core'],
    url='https://github.com/cfpb/eregs-2.0',
    license='CC0',
    description='The new version of eRegs.',
    include_package_data=True,
    install_requires=install_requires,
    setup_requires=setup_requires,
    frontend_build_script='setup.sh',
    extras_require={
        'testing': testing_extras,
    },
)
