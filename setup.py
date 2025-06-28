from setuptools import setup, find_namespace_packages

def parse_requirements(filename):
    with open(filename, 'r') as f:
        return f.read().splitlines()

setup(
    name='yggdrasil-go-gtk',
    version='0.1',
    package_data={
        "yggui.ui": ["*.ui", "*.css"],
    },
    packages=find_namespace_packages(include=['yggui*']),
    entry_points={
        'console_scripts': [
            'yggui=yggui.__main__:main',
        ],
    },
)
