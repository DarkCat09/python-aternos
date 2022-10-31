import setuptools

with open('README.md', 'rt') as readme:
    long_description = readme.read()

setuptools.setup(
    name='python-aternos',
    version='2.1.3',
    author='Chechkenev Andrey (@DarkCat09)',
    author_email='aacd0709@mail.ru',
    description='An unofficial Aternos API',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/DarkCat09/python-aternos',
    project_urls={
        'Documentation': 'https://python-aternos.codeberg.page',
        'GitHub': 'https://github.com/DarkCat09/python-aternos',
        'Bug Tracker': 'https://github.com/DarkCat09/python-aternos/issues',
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS',
        'Intended Audience :: Developers',
        'Topic :: Internet',
        'Typing :: Typed',
    ],
    install_requires=[
        'lxml>=4.8.0',
        'cloudscraper>=1.2.60',
        'js2py>=0.71',
        'websockets>=10.1',
        'regex>=2022.3.15',
    ],
    packages=['python_aternos'],
    python_requires=">=3.7",
)
