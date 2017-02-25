from setuptools import setup

setup(name='steamroller',
    version='1.0',
    description='Randomly picks Steam game to play next.',
    url='https://github.com/Sarmacid/steamroller',
    author='Sarmacid',
    author_email='sarmacid@users.noreply.github.com',
    license='GPLv3',
    packages=['steamroller', 'steamroller.lib'],
    install_requires=[
        'requests'
        ]
    )