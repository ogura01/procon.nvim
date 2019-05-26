import pynvim
from .atcoder.atcoder import AtCoder

import os
import sys

import glob
import subprocess

@pynvim.plugin
class Procon(object):
    def __init__(self, nvim):
        self.nvim = nvim

    def echom(self, args):
        self.nvim.command('echom "[PRO] {}"'.format(args))

    def get_root_dir_from_nvim(self):
        return self.nvim.call('procon#root_dir')

    def get_platform_from_nvim(self):
        return self.nvim.call('procon#platform')

    def root_dir(self):
        return '%s/%s' % (self.get_root_dir_from_nvim(), self.get_platform_from_nvim())

    def quickrun(self, script_path, filetype, args):
        argument = ' '.join(map(lambda x: str(x), args))
        command  = "QuickRun python3 -srcfile {} -filetype {} -args '{}'".format(script_path, filetype, argument)

        self.echom(command)
        self.nvim.command(command)

    def script_path(self, relative_path):
        platform = self.get_platform_from_nvim()
        return '%s/%s/%s' % (os.path.dirname(os.path.abspath(__file__)), platform, relative_path)

    @pynvim.command('ProUpdateContestList')
    def update_contest_list(self):
        script_path = self.script_path('update_contest_list.py')
        self.quickrun(script_path, '[quickrun]', [self.root_dir()])

    @pynvim.command('ProTest', nargs='*')
    def test(self, args):
        source_path = self.nvim.call('expand', '%:p')

        extensions = os.path.basename(source_path).split('.')
        extension = extensions[len(extensions) - 1]
        script_path = self.script_path('run_by_%s.py' % extension)

        index = args[0] if len(args) != 0 else -1

        self.quickrun(script_path, 'testrun', [source_path, index])

    @pynvim.function('ProJoinContest')
    def join_contest(self, args):
        contest_root = '%s/%s' % (self.root_dir(), args[0])

        script_path = self.script_path('join_contest.py')
        self.quickrun(script_path, '[quickrun]', [contest_root])
