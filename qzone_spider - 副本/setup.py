#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from distutils.core import setup

setup(name="qzone_spider",
      version="1.0.0.0",
      description="Spider of Qzone",
      author="Ding Junyao",
      author_email="dingjunyao0703@163.com",
      url="https://www.umutc.com/",
      license='GPLv3',
      packages=[''],
      long_description="""Really long text here.""",
      classifiers=[
        'Framework :: qzone_spider',
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GPLv3 License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.6',
    install_requires=[
        'selenium',
        'logging',
        're',
        'Pillow',
        'requests',
        'time',
        'json',
        'pymysql'],
)

