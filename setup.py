from setuptools import setup

setup(
    name='whodat',
    packages='whodat',
    version='0.1.0',
    author='Brad Berk',
    install_requires=[
        'espn_api>=0.31.0',
        'pandas==1.5.1',
        'numpy',
        'Django==3.2.8'
    ]
)
