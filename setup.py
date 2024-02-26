from setuptools import setup, find_packages

# Read the requirements from requirements.txt file
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='clashroyale_py',
    version='1.0.0',
    url='https://github.com/Davi-S/clashroyale_py',
    author='Davi Sampaio',
    author_email='davialvessampaio00@gmail.com',
    description='A python wrapper for the Clash Royale Official API',
    packages=find_packages(),    
    install_requires=requirements,
)