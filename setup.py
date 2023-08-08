import setuptools

with open('README.md', 'rt') as readme:
    long_description = readme.read()

setuptools.setup(
    name='python-aternos',
    version='4.0.0',
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
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Topic :: Internet',
        'Typing :: Typed',
    ],
    install_requires=[
        'selenium==4.11.0',
    ],
    extras_require={
        'dev': [
            'ruff==0.0.281',
        ],
        'pypi': [
            'build==0.10.0',
            'twine==4.0.2',
        ],
        'docs': [
            'mkdocs==1.4.3',
            'mkdocstrings[python]==0.22.0',
        ]
    },
    packages=['python_aternos'],
    python_requires=">=3.7",
)
