from setuptools import setup, find_packages

setup(
	name='expanserollbot',
	version='0.0.1',
	author='Mike Lang',
	author_email='mikelang3000@gmail.com',
	description='A discord bot for rolling dice for Expanse RPG',
	packages=find_packages(),
	install_requires=[
		'argh',
	],
)
