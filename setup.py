from distutils.core import setup
from setuptools import find_packages

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
    setup_requires=['cfgov_setup==1.2',],
    frontend_build_script='setup.sh'
)
