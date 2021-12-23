try:
    from setuptools.core import setup
except ImportError:
    from distutils.core import setup

setup(
    name='pcm_segmenter',
    version='0.0',
    author='Scott Sibole',
    packages=['pcm_segmenter'])
