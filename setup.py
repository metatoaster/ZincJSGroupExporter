from setuptools import setup
from setuptools import find_packages

version = '0.0.1'

classifiers = """
Development Status :: 3 - Alpha
Intended Audience :: Developers
Operating System :: OS Independent
Programming Language :: JavaScript
Programming Language :: Python :: 3
Programming Language :: Python :: 3.5
Programming Language :: Python :: 3.6
""".strip().splitlines()

package_json = {
    "dependencies": {
    },
    "devDependencies": {
        "eslint": "~3.15.0",
        "physiomeportal": "0.4.7",
    }
}

setup(
    name='zincjs_group_exporter',
    version=version,
    description='ZincJS Visualisation from PyZinc',
    long_description=open('README.md').read(),
    classifiers=classifiers,
    keywords='',
    author='Auckland Bioengineering Institute',
    url='https://github.com/alan-wu/scaffoldmaker-web-demo',
    packages=find_packages('src', exclude=['ez_setup']),
    package_dir={'': 'src'},
    namespace_packages=[],
    zip_safe=False,
    install_requires=[
        'setuptools>=12',
        'sqlalchemy>=0.9',
        # 'opencmiss.zinc',
        'requests',
        'sanic',
    ],
    extras_require={
        'webpack': [
            'calmjs.webpack>=1.2.0',
        ],
    },
    extras_calmjs={
        'node_modules': {
            'physiomeportal': 'physiomeportal/build/physiomeportal.frontend.js',
        },
    },

    package_json=package_json,
    calmjs_module_registry=['calmjs.module'],
    include_package_data=True,
    python_requires='>=3.5',
    build_calmjs_artifacts=True,
    entry_points={
        'console_scripts': [
            'zincjs_group_exporter = zincjs_group_exporter.app:main',
        ],
        'calmjs.module': [
            'zincjs_group_exporter = zincjs_group_exporter',
        ],
        'calmjs.artifacts': [
            'bundle.js = calmjs.webpack.artifact:complete_webpack',
        ],
    },
    # test_suite="",
)
