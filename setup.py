from setuptools import find_packages, setup


setup(
    name='imqfody',
    version='0.0.3',
    description='Python module for querying intelmq fody backend.',
    long_description=open('README.md').read(),
    author='Nils Kuhnert',
    author_email='nils@thehive-project.org',
    license='AGPL-V3',
    url='https://github.com/3c7/python-imqfody',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Programming Language :: Python :: 3',
    ],
    requires=[
        'requests'
    ]
)
