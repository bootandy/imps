from setuptools import setup


setup(
    name='imps',
    version='0.2.6',
    description='Python utility to sort Python imports',
    author='Andy Boot',
    author_email='bootandy@gmail.com',
    url='https://github.com/bootandy/imps',
    license="Apache",
    install_requires=['flake8-import-order', 'configparser'],
    packages=['imps'],
    entry_points={
        'console_scripts': [
            'imps = imps.shell:main',
        ],
    },
    keywords=['Refactoring', 'Imports'],
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Environment :: Console',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
    ]
)

# Command to upload to pypi:
# python setup.py sdist  upload -r https://www.python.org/pypi
# twine upload dist/*
