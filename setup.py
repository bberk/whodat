from setuptools import setup

setup(
    name='whodat',
    packages='whodat',
    version='0.1.0',
    author='Brad Berk',
    install_requires=[
        'espn_api>=0.21.1',
        'pandas==1.4.4',
        'numpy',
        'Django==3.2.8'
    ]
)
