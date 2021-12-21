#!/usr/bin/env python3
from setuptools import setup
from bepis_bot.version import __version__


def main():
  with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

  setup(
    name='bepis_bot',
    version=__version__,
    description='A plugin based bot framework',
    long_description=long_description,
    long_description_content_type='text/markdown',

    url='https://github.com/udf/bepis_bot',
    download_url='https://github.com/udf/bepis_bot',

    author='udf',
    author_email='tabhooked@gmail.com',

    license='AGPL',

    python_requires='>=3.6',
    keywords='telegram telethon bot framework',
    py_modules=['bepis_bot'],
    install_requires=['telethon']
  )


if __name__ == '__main__':
  main()