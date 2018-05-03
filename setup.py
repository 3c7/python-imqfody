from setuptools import setup


setup(
    name='imqfody',
    version='0.1.0',
    description='Python module for querying intelmq fody backend.',
    long_description=open('README.md').read(),
    author='Nils Kuhnert',
    author_email='nils@thehive-project.org',
    license='AGPL-V3',
    url='https://github.com/3c7/python-imqfody',
    packages=['imqfody'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Programming Language :: Python :: 3',
    ],
    requires=[
        'requests'
    ]
)
