from setuptools import setup

setup(
    name='Mail-Scheduler',
    version='0.1.0',
    packages=['app'],
    url='https://github.com/hveda/mail-scheduler',
    author='Heri Rusmanto',
    author_email='hvedaid@gmail.com',
    description='Automated mail sender scheduler',
    keywords=['mail', 'scheduler', 'scheduling', 'flask'],
    install_requires=[
        'flask>=0.10.1',
        'apscheduler>=3.2.0',
        'python-dateutil>=2.4.2'
    ],
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6'
    ]
)
