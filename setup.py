from setuptools import setup

setup(
    name='imps',
    version='0.1.0',
    description='Python utility to sort Python imports',
    author='Andy Boot',
    url='https://github.com/bootandy/imps',
    license="MIT",
    packages=['imps'],
    entry_points={
        'console_scripts': [
            'imps = imps.shell:main',
        ],
    }
    # scripts=['imps.shell']
)
