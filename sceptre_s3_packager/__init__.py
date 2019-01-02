import logging
from sceptre_s3_packager.s3_packager import KeyResolver, UploadHook  # noqa: F401, E501

__version__ = '0.1.0'
__author__ = 'Henrik Steen'


# Set up logging to ``/dev/null`` like a library is supposed to.
# http://docs.python.org/3.3/howto/logging.html#configuring-logging-for-a-library
class NullHandler(logging.Handler):  # pragma: no cover
    def emit(self, record):
        pass


logging.getLogger('sceptre_s3').addHandler(NullHandler())
