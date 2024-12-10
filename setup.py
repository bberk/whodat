from setuptools import setup

setup(
    name='whodat',
    packages=['whodat'],
    version='0.1.0',
    author='Brad Berk',
    install_requires=[
        'espn_api>=0.44.1',
        'pandas>=1.5.1',
        'numpy',
        'jinja2',
        'Django==3.2.8'
    ]
)
