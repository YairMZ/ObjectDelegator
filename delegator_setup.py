from setuptools import setup

setup(
    name='object-delegator',
    version='1.0',
    packages=['object-delegator'],
    url='https://github.com/YairMZ/OOP_utils',
    license='',
    author='Yair Mazal',
    author_email='mazaly@post.bgu.ac.il',
    description='This minimal yet powerful library allows delegation of an objects: methods, properties, and his own '
                'member objects, to an object who owns it. Recursive delegation is also supported.'
                'Use the simple API to handle delegations.',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
