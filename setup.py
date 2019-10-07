# -*- coding: utf-8 -*-
"""Setup script for django_custom_settings."""
import os

import yaml
from setuptools import find_packages, setup

try:  # for pip >= 10
    from pip._internal.req import parse_requirements
except ImportError:  # for pip <= 9.0.3
    from pip.req import parse_requirements


def get_version_info():
    """Get version from the version.py file"""
    from version import __version__

    return __version__


def setup_wheel():
    """Get requirements from files and set wheel information."""
    base_path = os.path.dirname(os.path.abspath(__file__))
    requirements = [
        str(ir.req)
        for ir in parse_requirements(
            os.path.join(base_path, "requirements", "base.txt"), session=False
        )
    ]
    requirements_test = [
        str(ir.req)
        for ir in parse_requirements(
            os.path.join(base_path, "requirements", "test.txt"), session=False
        )
    ]
    requirements_dev = [
        str(ir.req)
        for ir in parse_requirements(
            os.path.join(base_path, "requirements", "dev.txt"), session=False
        )
    ]
    extras_require = {
        "test": [r for r in requirements_test if r not in requirements],
        "dev": [r for r in requirements_dev if r not in requirements],
    }

    long_description = """Provide a Django interactive command for configuration file generation.
      See the project page for more information:
      https://github.com/ThomasMarques/django-settings-custom"""
    if os.path.isfile("README.md"):
        with open("README.md") as readme_file:
            long_description = readme_file.read()

    with open(".travis.yml") as travis_file:
        compatibility_information = yaml.load(travis_file)

    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Django",
    ]
    for django_version in compatibility_information["env"]:
        classifiers.append("Framework :: Django :: %s" % django_version.split("=")[1])
    classifiers.extend(
        [
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
            "Programming Language :: Python",
        ]
    )
    python_versions = set()
    for python_version in compatibility_information["python"]:
        python_versions.add(python_version[:1])
        python_versions.add(python_version)
    classifiers.extend(
        sorted(["Programming Language :: Python :: %s" % v for v in python_versions])
    )
    classifiers.extend(
        [
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: Implementation :: CPython",
            "Programming Language :: Python :: Implementation :: PyPy",
            "Topic :: Utilities",
        ]
    )

    setup(
        name="django-settings-custom",
        version=get_version_info(),
        description="A Django interactive command for configuration file generation.",
        long_description=long_description,
        long_description_content_type="text/markdown",
        author="Thomas Marques",
        author_email="marquesthom@gmail.com",
        license="MIT License",
        platforms=["any"],
        url="https://github.com/ThomasMarques/django-settings-custom",
        packages=find_packages(where="."),
        include_package_data=True,
        install_requires=requirements,
        extras_require=extras_require,
        classifiers=classifiers,
    )


setup_wheel()
