import setuptools

with open('README.md', 'rt') as readme:
    long_description = readme.read()

setuptools.setup(
    name='python-aternos',
    version='0.1',
    author='Chechkenev Andrey (@DarkCat09)',
    author_email='aacd0709@mail.ru',
    description='An unofficial Aternos API',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/DarkCat09/python-aternos',
    project_urls={
        'Bug Tracker': 'https://github.com/DarkCat09/python-aternos/issues',
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent'
    ],
    install_requires=[
        'lxml==4.6.2',
        'requests==2.25.1',
        'cloudscraper==1.2.58'
    ],
    python_requires=">=3.6",
)
