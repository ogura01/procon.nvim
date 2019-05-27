from atcoder import AtCoder

import os

if __name__ == '__main__':
    source_path = os.path.expanduser('~/.procon/atcoder/abc128/a.cpp')
    problem_key = os.path.basename(source_path).split('.')[0]
    contest_dir = os.path.dirname(source_path)
    root_dir = os.path.dirname(contest_dir)

    atcoder = AtCoder(root_dir)

    print(source_path)
    print(contest_dir)
    print(root_dir)


