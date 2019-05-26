# ============================================================================
# FILE: problem.py
# AUTHOR: ogura01 (ogura01@gmail.com)
# License: MIT license
# ============================================================================

from denite.base.source import Base
from procon.atcoder import AtCoder

import os

CONTEST_LIST_HIGHLIGHT_SYNTAX = [
    {'name': 'Time', 'link': 'PreProc',  're': r'\[.\{-}\] '},
    {'name': 'Name', 'link': 'Constant', 're': r'(.\{-})'},
]

class Source(Base):
    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'problem'
        self.kind = 'directory'

    def highlight(self):
        for syn in CONTEST_LIST_HIGHLIGHT_SYNTAX:
            self.vim.command(
                'syntax match {0}_{1} /{2}/ contained containedin={0}'.format(
                    self.syntax_name, syn['name'], syn['re']))
            self.vim.command(
                'highlight default link {}_{} {}'.format(
                    self.syntax_name, syn['name'], syn['link']))

    def gather_candidates(self, context):
        root_dir = self.vim.call("procon#root_dir")

        atcoder = AtCoder(root_dir)
        atcoder.load()

        return list(map(lambda problem: self.calc_candidate_from(problem), atcoder.problems()))

    def calc_candidate_from(self, problem):
        contest = problem.contest_key()
        key   = problem.problem_key().upper()
        name  = problem.name()
        score = problem.score()

        word = '[%s] %s: %s - %s' % (score, key, name, contest)
        return { 'name': name, 'word': word, 'action__path': problem.contest.root_dir() }

