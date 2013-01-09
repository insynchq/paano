from setuptools import setup


setup(
    name='paano',
    version='0.0.0',
    url='http://github.com/marksteve/paano',
    license='MIT',
    author='Mark Steve Samson',
    author_email='marksteve@insynchq.com',
    description='Dead simple FAQ/HowTo CMS',
    long_description=__doc__,
    packages=['paano'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask==0.9',
        'Flask-Babel==0.8',
        'Flask-SQLAlchemy==0.16',
        'Flask-WTF==0.8.2',
        'Flask-GoogleLogin==0.0.3',
        'misaka==1.0.2',
    ],
    classifiers=[
    ],
)
