# -*- coding: utf-8 -*-

try:  # for pip >= 10
    from pip._internal.req import parse_requirements
except ImportError:  # for pip <= 9.0.3
    from pip.req import parse_requirements
from setuptools import find_packages, setup

requirements = [str(ir.req) for ir in parse_requirements('requirements.txt', session=False)]
requirements_test = [r for r in [str(ir.req) for ir in parse_requirements('requirements-dev.txt', session=False)]
                     if r not in requirements]


def get_version_info():
    return '1.0.0'


setup(
    name='django-settings-custom',
    version=get_version_info(),
    url='https://github.com/ThomasMarques/django-settings-custom',
    packages=find_packages(where='.',),
    include_package_data=True,
    install_requires=requirements,
    extras_require={'test': requirements_test}
)
