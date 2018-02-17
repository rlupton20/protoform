from setuptools import setup

setup(
    name="protoform",
    version="0.0.1",
    author="Richard Lupton",
    description="A combinatorial parsing library",
    license="BSD",
    keywords="parsing",
    packages=["protoform"],
    python_requires=">=3",
    setup_requires=['pytest-runner'],
    tests_require=['pytest']
)
