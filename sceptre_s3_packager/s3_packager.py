from botocore.exceptions import ClientError
from sceptre.connection_manager import ConnectionManager
from sceptre.hooks import Hook
from sceptre.resolvers import Resolver
import hashlib
import logging
import os
import zipfile

try:
    from StringIO import StringIO as BufferIO
except ImportError:
    from io import BytesIO as BufferIO

try:
    import zlib  # noqa: F401

    compression = zipfile.ZIP_DEFLATED
except ImportError:
    compression = zipfile.ZIP_STORED


def get_s3_name(md5):
    return 'sceptre/{}'.format(md5.hexdigest())


class KeyResolver(Resolver):
    def __init__(self, *args, **kwargs):
        super(KeyResolver, self).__init__(*args, **kwargs)

    def resolve(self):
        return self.get_s3_key(self.argument)

    def get_s3_key(self, dir):
        content = Zipper().zip_dir(dir)

        md5 = hashlib.new('md5')
        md5.update(content)

        s3_key = get_s3_name(md5)

        return s3_key


class UploadHook(Hook):
    DELIMITER = '^^'

    def __init__(self, *args, **kwargs):
        super(UploadHook, self).__init__(*args, **kwargs)

    def run(self):
        src_dir, s3_bucket = self.get_arguments()

        content = Zipper().zip_dir(src_dir)

        md5 = hashlib.new('md5')
        md5.update(content)

        s3_key = get_s3_name(md5)

        self.logger.debug('{} resolved to s3://{}/{}'.format(
            src_dir, s3_bucket, s3_key
        ))

        # The docs say this is available on the Stack instance, but it
        # is not always initialized.
        connection_manager = ConnectionManager(
            self.stack.region, self.stack.profile, self.stack.external_name
        )

        try:
            connection_manager.call(
                service='s3',
                command='head_object',
                kwargs={
                    'Bucket': s3_bucket,
                    'Key': s3_key
                },
            )

            self.logger.debug('s3://{}/{} already up to date'.format(
                s3_bucket, s3_key
            ))
        except ClientError as e:
            if e.response['Error']['Code'] not in ['404', '412']:
                raise e

            self.logger.debug('putting {} to s3://{}/{}'.format(
                src_dir, s3_bucket, s3_key
            ))

            connection_manager.call(
                service='s3',
                command='put_object',
                kwargs={
                    'Bucket': s3_bucket,
                    'Key': s3_key,
                    'Body': content
                },
            )

            self.logger.debug('s3://{}/{} put for {}'.format(
                s3_bucket, s3_key, src_dir
            ))

    def get_arguments(self):
        if self.DELIMITER in self.argument:
            src_dir, s3_bucket = self.argument.split(self.DELIMITER, 1)
            return src_dir, s3_bucket

        code = self.stack.sceptre_user_data.get('Code', {})

        src_dir = self.argument
        s3_bucket = code.get('S3Bucket')

        if isinstance(s3_bucket, Resolver):
            s3_bucket = s3_bucket.resolve()

        return src_dir, s3_bucket


class Zipper:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def zip_dir(self, dirpath):
        files = sorted([
            os.path.relpath(
                os.path.join(root, file),
                dirpath
            )
            for root, _, files in os.walk(dirpath)
            for file in files
        ])

        if (len(files) == 0):
            raise Exception('No files found in {}'.format(dirpath))

        buffer = BufferIO()

        with zipfile.ZipFile(buffer, mode="w", compression=compression) as zf:
            for file in files:
                real_file = os.path.join(dirpath, file)
                self.logger.info("zipping file {}".format(real_file))
                self.write_file_to_zip(zf, real_file, file)

        buffer.seek(0)
        return buffer.read()

    def write_file_to_zip(self, zf, filename, arcname):
        st = os.stat(filename)

        zinfo = zipfile.ZipInfo(arcname, (2018, 1, 1, 0, 0, 0))
        zinfo.external_attr = (st[0] & 0xFFFF) << 16  # Unix attributes

        content = self.read_file(filename)

        zf.writestr(zinfo, content)

    def read_file(self, filename):
        with open(filename, "rb") as fp:
            return fp.read()
