"""
paano
=====

Dead simple FAQ/HowTo CMS
"""

from setuptools import setup


setup(
    name='paano',
    version='0.1.2',
    url='http://github.com/marksteve/paano',
    license='MIT',
    author='Mark Steve Samson',
    author_email='marksteve@insynchq.com',
    description='Dead simple FAQ/HowTo CMS',
    long_description=__doc__,
    packages=['paano'],
    zip_safe=False,
    include_package_data=True,
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
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
    ],
)
