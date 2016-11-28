import os
from setuptools import setup



def read(relpath: str) -> str:
	with open(os.path.join(os.path.dirname(__file__), relpath)) as f:
		return f.read()


setup(
	name = 'aiodebug',
	version = read('version.txt').strip(),
	description = 'A tiny library for monitoring and testing asyncio programs',
	long_description = read('README.rst'),
	author = 'Quantlane',
	author_email = 'code@quantlane.com',
	url = 'https://github.com/qntln/aiodebug',
	license = 'Apache 2.0',
	extras_require = {
		'logwood': ['logwood>=3.0.0,<4.0.0'],
	},
	packages = [
		'aiodebug',
		'aiodebug.testing',
	],
	classifiers = [
		'Development Status :: 4 - Beta',
		'License :: OSI Approved :: Apache Software License',
		'Natural Language :: English',
		'Programming Language :: Python :: 3 :: Only',
		'Programming Language :: Python :: 3.5',
	]
)
