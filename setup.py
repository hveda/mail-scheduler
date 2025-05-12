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
        'flask>=2.3.2',
        'apscheduler>=3.10.4',
        'python-dateutil>=2.8.2',
        'flask-sqlalchemy>=3.1.1',
        'Flask-Mail>=0.9.1',
        'Flask-Migrate>=4.0.5',
        'Flask-RQ2>=18.3',
        'Flask-SQLAlchemy>=3.1.1',
        'pytest>=7.4.3',
        'pytest-flask>=1.3.0',
        'pytest-cov>=4.1.0'
    ],
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12'
    ],
    python_requires='>=3.10'
)
