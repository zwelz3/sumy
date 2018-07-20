#
#
#
#
import os
import stat


def is_hidden(filepath):
    return bool(os.stat(filepath).st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN)


def get_path(filepath, filename):
    return os.path.join(filepath, filename)
