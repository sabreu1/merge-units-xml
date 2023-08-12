from setuptools import setup, find_packages

setup(
    name="merge-units-xml",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'tqdm',
        # any other dependencies you might have
    ],
    entry_points={
        'console_scripts': [
            'merge-units-xml = src.main:main',  # If you want to create a command-line tool
        ],
    },
)
