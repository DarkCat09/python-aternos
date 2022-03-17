import setuptools

with open('README.md', 'rt') as readme:
	long_description = readme.read()

with open('requirements.txt', 'rt') as f:
	requires = f.readlines()
	for i, r in enumerate(requires):
		requires[i] = r.strip('\r\n')

setuptools.setup(
	name='python-aternos',
	version='0.6',
	author='Chechkenev Andrey (@DarkCat09)',
	author_email='aacd0709@mail.ru',
	description='An unofficial Aternos API',
	long_description=long_description,
	long_description_content_type='text/markdown',
	url='https://github.com/DarkCat09/python-aternos',
	project_urls={
		'Bug Tracker': 'https://github.com/DarkCat09/python-aternos/issues',
		'Documentation': 'https://github.com/DarkCat09/python-aternos/wiki/Client-(entry-point)',
	},
	classifiers=[
		'Development Status :: 4 - Beta',
		'Programming Language :: Python :: 3',
		'License :: OSI Approved :: Apache Software License',
		'Operating System :: OS Independent'
	],
	install_requires=requires,
	packages=['python_aternos'],
	python_requires=">=3.7",
)
