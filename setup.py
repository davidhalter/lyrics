#!/usr/bin/env python

from setuptools import setup, find_packages

from lyrics import version, __project__, __license__


with open('README.rst') as f:
    readme = f.read()

with open('requirements.txt', 'r') as f:
    lines = f.readlines()
    install_requires = [l.strip().strip('\n') for l in lines if l.strip()
                                        and not l.strip().startswith('#')]

meta = dict(
    name=__project__,
    version=version,
    license=__license__,
    description='Play music and view the lyrics.',
    long_description=readme,
    platforms=('Any'),

    author='David Halter',
    url=' http://github.com/davidhalter/lyrics',

    packages=find_packages(),
    include_package_data=True,

    entry_points={
        'console_scripts': [
            'lyrics = lyrics.main',
        ]
    },

    install_requires=install_requires,
    test_suite = 'test',
)


if __name__ == "__main__":
    setup(**meta)
