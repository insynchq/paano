from setuptools import setup


setup(
    name='paano',
    version='0.0.0',
    url='http://github.com/marksteve/paano',
    license='MIT',
    author='Mark Steve Samson',
    author_email='marksteve@insynchq.com',
    description='Simple FAQ manager',
    long_description=__doc__,
    packages=['paano'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask==0.9',
        'Flask-SQLAlchemy',
        'Flask-WTF',
        'Flask-Babel',
    ],
    classifiers=[
    ],
)
