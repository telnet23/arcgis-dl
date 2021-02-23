#!/usr/bin/env python

import os
import setuptools

path = os.path.dirname(os.path.abspath(__file__))

setuptools.setup(
    name='arcgis-dl',
    description='',
    long_description=os.path.join(path, 'README.md').read_file(),
    long_description_content_type='text/markdown',
    license='Apache License 2.0',
    use_scm_version=True,
    setup_requires=[
        'setuptools_scm',
    ],
    packages=[
        'arcgis_dl',
    ],
    entry_points={
        'console_scripts': [
            'arcgis-dl = arcgis_dl.__main__:main',
        ],
    },
    classifiers=[
        'Topic :: Scientific/Engineering :: GIS',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
    ],
)
