import setuptools
from sceptre_s3_packager import __version__

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='sceptre_s3_packager',
    version=__version__,
    author='Henrik Steen',
    description='S3 packager for Sceptre 2',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/henrist/sceptre-s3-packager',
    install_requires=['sceptre>=2'],
    packages=setuptools.find_packages(),
    entry_points={
        'sceptre.hooks': [
            'sceptre_s3_upload = sceptre_s3_packager.s3_packager:UploadHook',
        ],
        'sceptre.resolvers': [
            'sceptre_s3_key = sceptre_s3_packager.s3_packager:KeyResolver',
        ]
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License'
    ],
)
