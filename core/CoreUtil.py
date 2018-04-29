import sys

from cement.utils import shell
import hashlib


class CoreUtil:
    BLOCK_SIZE = 65536

    @classmethod
    def hash(cls, file_path):
        sha256 = hashlib.sha256()
        md5 = hashlib.md5()
        with open(file_path, 'rb') as afile:
            buf = afile.read(CoreUtil.BLOCK_SIZE)
            while len(buf) > 0:
                md5.update(buf)
                sha256.update(buf)
                buf = afile.read(CoreUtil.BLOCK_SIZE)
        print('SHA256 hash:')
        print(file_path, sha256.hexdigest())
        print('MD5 hash:')
        print(file_path, md5.hexdigest())
