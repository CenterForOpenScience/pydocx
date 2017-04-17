from six import StringIO, BytesIO


def get_stream_cls(data):
    if isinstance(data, bytes):
        buf_cls = BytesIO
    else:
        buf_cls = StringIO

    return buf_cls
