from setuptools import setup, find_namespace_packages

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
