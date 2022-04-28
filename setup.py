import setuptools

with open('README.md', 'rt') as readme:
	long_description = readme.read()

setuptools.setup(
	name='python-aternos',
	version='1.0.1',
	author='Chechkenev Andrey (@DarkCat09)',
	author_email='aacd0709@mail.ru',
	description='An unofficial Aternos API',
	long_description=long_description,
	long_description_content_type='text/markdown',
	url='https://github.com/DarkCat09/python-aternos',
	project_urls={
		'Bug Tracker': 'https://github.com/DarkCat09/python-aternos/issues',
		'Alternative Repo': 'https://codeberg.org/DarkCat09/python-aternos'
	},
	classifiers=[
		'Development Status :: 4 - Beta',
		'Programming Language :: Python :: 3',
		'License :: OSI Approved :: Apache Software License',
		'Operating System :: OS Independent'
	],
	install_requires=[
		'lxml>=4.8.0',
		'cloudscraper>=1.2.58',
		'js2py>=0.71',
		'websockets>=10.1',
		'regex>=2022.3.15'
	],
	packages=['python_aternos'],
	python_requires=">=3.7",
)
