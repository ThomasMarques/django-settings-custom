# -*- coding: utf-8 -*-
import os
import yaml

try:  # for pip >= 10
    from pip._internal.req import parse_requirements
except ImportError:  # for pip <= 9.0.3
    from pip.req import parse_requirements
from setuptools import find_packages, setup

requirements = [str(ir.req) for ir in parse_requirements('requirements.txt', session=False)]
requirements_test = [r for r in [str(ir.req) for ir in parse_requirements('requirements-dev.txt', session=False)]
                     if r not in requirements]

long_description = """Provide a Django interactive command for configuration file generation.
  See the project page for more information:
  https://github.com/ThomasMarques/django-settings-custom"""
if os.path.isfile("README.md"):
    with open("README.md") as f:
        long_description = f.read()


def get_version_info():
    from version import __version__
    return __version__


with open('.travis.yml') as travis_file:
    compatibility_information = yaml.load(travis_file)

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Environment :: Web Environment',
    'Framework :: Django',
]
for django_version in compatibility_information['env']:
    classifiers.append('Framework :: Django :: %s' % django_version.split('=')[1])
classifiers.extend([
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python'
])
python_versions = set()
for python_version in compatibility_information['python']:
    python_versions.add(python_version[:1])
    python_versions.add(python_version)
classifiers.extend(sorted(['Programming Language :: Python :: %s' % v for v in python_versions]))
classifiers.extend([
    'Programming Language :: Python :: Implementation :: CPython',
    'Programming Language :: Python :: Implementation :: PyPy',
    'Topic :: Utilities',
])

setup(
    name='django-settings-custom',
    version=get_version_info(),
    description="A Django interactive command for configuration file generation.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Thomas Marques',
    author_email='marquesthom@gmail.com',
    license='MIT License',
    platforms=['any'],
    url='https://github.com/ThomasMarques/django-settings-custom',
    packages=find_packages(where='.',),
    include_package_data=True,
    install_requires=requirements,
    extras_require={'test': requirements_test},
    classifiers=classifiers
)
