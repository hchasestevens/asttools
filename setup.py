from setuptools import setup
 
setup(
    name='asttools',
    packages=['asttools'],
    version='0.1.2',
    description='Tools for AST construction and manipulation',
    license='MIT',
    author='H. Chase Stevens',
    author_email='chase@chasestevens.com',
    url='https://github.com/hchasestevens/asttools',
    install_requires=[
        'astor',
        'meta'
    ],
    entry_points={},
    keywords='ast asts syntax metaprogramming',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
    ]
)
