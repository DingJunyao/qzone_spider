from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='qzone_spider',
      version='1.0.0',
      description='Spider of Qzone',
      long_description=long_description,
      long_description_content_type='text/markdown',
      author='Ding Junyao',
      author_email='dingjunyao0703@163.com',
      url='https://github.com/DingJunyao/qzone_spider',
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: Education',
          'Intended Audience :: Information Technology',
          'Intended Audience :: Legal Industry',
          'Intended Audience :: Science/Research',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: SQL',
          'Topic :: Scientific/Engineering :: Information Analysis',
          'Topic :: Sociology',
          'Topic :: Utilities',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      keywords='spider Qzone QQ SNS data mining crawler',
      packages=find_packages(exclude=['contrib', 'docs', 'tests']),
      package_data={
          'qzone_spider': ['emotion.csv'],
      },
      entry_points={
        'console_scripts': [
            'qzone_spider = qzone_spider.spider:main',
            'qzone-spider = qzone_spider.spider:main',
        ],
      },
      python_requires='>=3.6',
      install_requires=[
          'selenium',
          'requests'
      ],
      extras_require={
        'mysql': ['pymysql'],
        'postgresql': ['psycopg2'],
        },
      )
