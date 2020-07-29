from setuptools import setup

setup(
    name='ObjectDelegator',
    version='1.0',
    packages=['ObjectDelegator'],
    url='https://github.com/YairMZ/ObjectDelegator',
    license='GNU General Public License v3.0',
    author='Yair Mazal',
    author_email='mazaly@post.bgu.ac.il',
    description='This minimal yet powerful library allows delegation of an objects: methods, properties, and his own '
                'member objects, to an object who owns it. Recursive delegation is also supported.'
                'Use the simple API to handle delegations.',
    download_url='https://github.com/YairMZ/ObjectDelegator/archive/v1.0.tar.gz',
    keywords=['OOP', 'delegation', 'composition'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Topic :: Software Development :: Object Brokering",
    ],
    python_requires='>=3.8',
)
