from setuptools import find_packages, setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="bardolph",
    version="0.0.5",
    author="Al Fontes",
    author_email="bardolph@fontes.org",
    description="Simple script interpreter for LIFX light bulbs",
    url="https://github.com/al-fontes-jr/bardolph",
    license = 'Apache License 2.0',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=[
        'bardolph.controller', 'bardolph.parser', 'bardolph.lib',
        'bardolph.fakes'],
    install_requires=['lifxlan'],
    python_requires='>=3.5',
    entry_points={
        'console_scripts': [
            'lsrun=bardolph.controller:run.main',
            'lsnap=bardolph.controller:snapshot.main',
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha"
    ],
)
