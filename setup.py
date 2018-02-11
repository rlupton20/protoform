from distutils.core import setup

setup(
    name="python-parser",
    version="0.0.1",
    author="Richard Lupton",
    description="A combinatorial parsing library",
    license="BSD",
    keywords="parsing",
    packages=["python_parser"],
    python_requires=">=3",
    setup_requires=['pytest-runner'],
    tests_require=['pytest']
)
