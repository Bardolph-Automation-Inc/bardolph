from setuptools import setup

with open("README.md", "r") as f:
    long_description_md = f.read()

setup(
    name="bardolph",
    version="0.0.33",
    author="Al Fontes",
    author_email="bardolph@fontes.org",
    description="Simple script interpreter for LIFX light bulbs",
    long_description=long_description_md,
    long_description_content_type='text/markdown',
    url="http://www.bardolph.org",
    license='Apache License 2.0',
    packages=[
        'bardolph.controller', 'bardolph.parser', 'bardolph.lib',
        'bardolph.fakes'],
    install_requires=['lifxlan'],
    python_requires='>=3.5',
    entry_points={
        'console_scripts': [
            'lsc=bardolph.controller:lsc.main',
            'lscap=bardolph.controller:snapshot.main',
            'lsrun=bardolph.controller:run.main',
            'lsparse=bardolph.parser:parse.main'
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha"
    ],
)
