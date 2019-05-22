import pynvim
from .atcoder import AtCoder

import os
import sys

import glob
import subprocess

@pynvim.plugin
class Procon(object):
    def __init__(self, nvim):
        self.nvim = nvim

        root_dir = self.get_root_dir_from_nvim()
        self.atcoder = AtCoder(root_dir)

    def echom(self, args):
        self.nvim.command('echom "[PRO] {}"'.format(args))

    def write(self, args):
        if args.strip() != '':
            self.echom(args)

    def flush(self):
        return None

    def get_root_dir_from_nvim(self):
        return self.nvim.call('procon#root_dir')

    @pynvim.command('ProUpdateContestList')
    def update_contest_list(self, args):
        self.atcoder.update(is_force = True)

        for contest in self.atcoder.contests:
            self.echom(contest.inspect())

    @pynvim.command('ProTest', nargs='*')
    def test(self, args):
        source_path = self.nvim.call('expand', '%:p')
        extensions = os.path.basename(source_path).split('.')
        extension = extensions[len(extensions) - 1]

        script_path = os.path.dirname(os.path.abspath(__file__))
        script_path = '%s/%s_runner_for_atcoder.py' % (script_path, extension)

        index = args[0] if len(args) != 0 else -1

        command = "QuickRun python3 -srcfile {} -filetype testrun -args '{} {}'".format(script_path, source_path, index)
        self.echom(command)
        self.nvim.command(command)

    @pynvim.function('ProUpdateRootDir')
    def update_root_dir(self, args):
        root_dir = self.get_root_dir_from_nvim()
        self.atcoder.set_root_dir(root_dir)

    @pynvim.function('ProJoinContest')
    def join_contest(self, args):
        sys.stdout = self

        contest_key = args[0]

        self.echom('contest_key: {}'.format(contest_key))
        contest = self.atcoder.find_or_create_contest(contest_key)

        if contest:
            self.echom(contest.inspect())

            try:
                contest.update()
            except Exception as e:
                self.echom(e)
                self.echom(sys.exc_info())

            command = 'cd {}'.format(contest.root_dir())
            self.echom(command)
            self.nvim.command(command)

        self.echom('Done')

        sys.stdout = sys.__stdout__
