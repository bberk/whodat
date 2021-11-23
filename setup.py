from setuptools import setup

setup(
    name='whodat',
    packages='whodat',
    version='0.1.0',
    author='Brad Berk',
    install_requires=[
        'espn_api>=0.19.0',
        'pandas==1.3.4',
        'numpy',
        'Django==3.2.8'
    ]
)
