# coding: utf-8

from atcoder import AtCoder

import sys
import os

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        raise Exception('please, input root_dir to args!')

    atcoder = AtCoder(os.path.abspath(sys.argv[1]))
    atcoder.update(is_force=True)
