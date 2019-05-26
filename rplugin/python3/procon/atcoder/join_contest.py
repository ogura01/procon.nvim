# coding: utf-8

from atcoder import AtCoder, Contest, Problem

import sys
import os

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        raise Exception('please, input contest_root to args!')

    contest_root = sys.argv[1]
    contest_key  = os.path.basename(contest_root)

    print(contest_root)

    root_dir = os.path.dirname(contest_root)
    atcoder = AtCoder(root_dir)

    contest = atcoder.find_or_create_contest(contest_key)

    if contest:
        print(contest.inspect())

        try:
            contest.update()
        except Exception as e:
            print(e)
            print(sys.exc_info())

        command = 'cd {}'.format(contest.root_dir())
        print(command)

    print('Done')
