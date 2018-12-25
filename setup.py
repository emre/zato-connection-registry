from setuptools import setup

setup(
    name='zato-connection-registry',
    version='0.0.2',
    packages=[
        'zato_connection_registry',
    ],
    url='https://github.com/emre/zato-connection-registry',
    license='MIT',
    author='emre yilmaz',
    author_email='mail@emreyilmaz.me',
    description='Load/Backup/Restore your Zato connections',
    entry_points={
        'console_scripts': [
            'zato_connection_registry = zato_connection_registry.cli:main',
        ],
    },
    install_requires=["zato-client==3.0.2", "click", "responses"]
)