import logging

__version__ = '0.3.0'
__author__ = 'Henrik Steen'


# Set up logging to ``/dev/null`` like a library is supposed to.
# http://docs.python.org/3.3/howto/logging.html#configuring-logging-for-a-library
class NullHandler(logging.Handler):  # pragma: no cover
    def emit(self, record):
        pass


logging.getLogger('sceptre_s3_packager').addHandler(NullHandler())
