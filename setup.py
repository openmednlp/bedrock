from setuptools import setup, find_packages
import pypandoc

# Get the long description from the README file
with open('README.md', encoding='utf-8') as f:
    long_description = pypandoc.convert(f.read(), "rst", format="md")

with open('requirements.txt') as f:
    reqs = f.read().splitlines()

setup(
    name='bedrock',
    version='0.1.0.dev11',
    description=("Bedrock is a high-level text pre-processing API, "
                 "written in Python and can run on NLTK or Spacy "
                 "as its backends."),
    long_description=long_description,
    keywords='nlp pre-processing text',
    author='Ivan Nesic',
    author_email='ivan.nesic@usb.ch',
    url='http://github.com/openmednlp/bedrock',
    python_requires='>=3',
    packages=find_packages(include=['bedrock', 'bedrock.*']),
    install_requires=reqs,
    license='MIT',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Topic :: Text Processing :: Linguistic',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    scripts=['bin/bedrock'],
)
