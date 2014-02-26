# setup.py
import ez_setup
ez_setup.use_setuptools()
from setuptools import setup

setup(name='devops',
      version='0.0.1',
      author='Chris Zacny',
      author_email='chris@chriszacny.com',
      url='http://chriszacny.com/projects/',
      packages=['devops', 'devops.workflow', 'devops.workflow.tasks'],
      package_data={'devops.workflow': ['*.cfg']},
      install_requires=['requests', 'xlrd', 'colorama'],
)