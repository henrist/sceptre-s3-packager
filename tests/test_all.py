from botocore.exceptions import ClientError
from mock import MagicMock, patch, call
from sceptre_s3_packager.s3_packager import KeyResolver, UploadHook
from sceptre.stack import Stack


class TestKeyResolver(object):
    def setup_method(self, method):
        self.key_resolver = KeyResolver()
        self.key_resolver.argument = './tests/testdata'

    def test_simple(self):
        key = self.key_resolver.resolve()

        assert key == 'sceptre/55cdcd252b548216c5b4a0088de166b8'


class TestUploadHook(object):
    def setup_method(self, method):
        self.upload_hook = UploadHook()
        self.upload_hook.argument = './tests/testdata'

        self.upload_hook.stack = MagicMock(spec=Stack)
        self.upload_hook.stack.region = 'eu-central-1'
        self.upload_hook.stack_stack_name = 'my-stack'
        self.upload_hook.stack.profile = None
        self.upload_hook.stack.external_name = None

        self.upload_hook.stack.sceptre_user_data = {
            'Code': {
                'S3Bucket': 'my-bucket'
            }
        }

    @patch('sceptre.connection_manager.ConnectionManager.call')
    def test_with_upload(self, mock_call):
        mock_call.side_effect = [ClientError({
            'Error': {
                'Code': '404'
            }
        }, 'dummy'), None]

        self.upload_hook.run()

        mock_call.assert_has_calls([
            call(
                service='s3',
                command='head_object',
                kwargs={
                    'Bucket': 'my-bucket',
                    'Key': 'sceptre/55cdcd252b548216c5b4a0088de166b8'
                },
            ),
            call(
                service='s3',
                command='put_object',
                kwargs={
                    'Bucket': 'my-bucket',
                    'Key': 'sceptre/55cdcd252b548216c5b4a0088de166b8',
                    'Body': b'PK\x03\x04\x14\x00\x00\x00\x00\x00\x00\x00!L\xbd\xbf\x0cg\x1e\x00\x00\x00\x1e\x00\x00\x00\x0b\x00\x00\x00my_file.txtContent for automated testing\nPK\x01\x02\x14\x03\x14\x00\x00\x00\x00\x00\x00\x00!L\xbd\xbf\x0cg\x1e\x00\x00\x00\x1e\x00\x00\x00\x0b\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xa4\x81\x00\x00\x00\x00my_file.txtPK\x05\x06\x00\x00\x00\x00\x01\x00\x01\x009\x00\x00\x00G\x00\x00\x00\x00\x00'  # noqa: E501
                },
            )
        ])

    @patch('sceptre.connection_manager.ConnectionManager.call')
    def test_without_upload(self, mock_call):
        self.upload_hook.run()

        mock_call.assert_has_calls([
            call(
                service='s3',
                command='head_object',
                kwargs={
                    'Bucket': 'my-bucket',
                    'Key': 'sceptre/55cdcd252b548216c5b4a0088de166b8'
                },
            ),
        ])
