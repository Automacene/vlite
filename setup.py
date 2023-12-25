from setuptools import setup, find_packages

setup(
    name='vlite',
    version='0.2.0',
    author='Codie Petersen',
    description='A simple vector database that stores vectors in a numpy array. Remixed by Atuomacene.',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'vlite=gui.cli:main',
        ],
    },
    install_requires=[
        'numpy',
        'pysbd',
        'PyPDF2',
        'transformers',
        'torch',
        'uuid'
    ],
)
