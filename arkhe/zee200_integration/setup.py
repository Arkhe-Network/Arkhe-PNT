from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup, find_packages
import os
import sys

# Configurar paths para headers e libs do ZEE200
ZEE200_ROOT = os.environ.get('ZEE200_ROOT', '../ZEE200')
include_dirs = [
    os.path.join(ZEE200_ROOT, 'include'),
    os.path.join(ZEE200_ROOT, 'external/emp-tool/include'),
    'include',
]

library_dirs = [os.path.join(ZEE200_ROOT, 'build/lib')]
libraries = ['gtzk_cpu', 'emp_zk', 'emp_ot']

ext_modules = [
    Pybind11Extension(
        "zee200_backend",
        ["zee200_bindings.cpp"],
        include_dirs=include_dirs,
        library_dirs=library_dirs,
        libraries=libraries,
        cxx_std=17,
        extra_compile_args=['-O3', '-march=native'],
        define_macros=[('FIELD_MERSENNE_61', '1'), ('SECURITY_BITS', '40')],
    ),
]

setup(
    name="zee200-arkhe",
    version="0.1.0",
    author="Rafael Oliveira",
    author_email="raf@arkhe.network",
    description="ZEE200 backend bindings for ARKHE OS via pybind11",
    long_description=open('README.md').read() if os.path.exists('README.md') else '',
    long_description_content_type='text/markdown',
    ext_modules=ext_modules,
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    cmdclass={"build_ext": build_ext},
    python_requires='>=3.8',
    install_requires=['numpy>=1.20', 'scipy>=1.7'],
    extras_require={
        'dev': ['pytest>=7.0', 'black>=22.0', 'mypy>=0.990'],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Scientific/Engineering :: Mathematics',
    ],
)
