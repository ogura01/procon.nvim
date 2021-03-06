# ============================================================================
# FILE: contest.py
# AUTHOR: ogura01 (ogura.nop@gmail.com)
# License: MIT license
# ============================================================================

from denite.base.source import Base
from procon.atcoder.atcoder import AtCoder

CONTEST_LIST_HIGHLIGHT_SYNTAX = [
    {'name': 'Time', 'link': 'PreProc',  're': r'\[.\{-}\] '},
    {'name': 'Name', 'link': 'Constant', 're': r'(.\{-})'},
]


class Source(Base):
    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'contest'
        self.kind = 'contest'

    def highlight(self):
        for syn in CONTEST_LIST_HIGHLIGHT_SYNTAX:
            self.vim.command(
                'syntax match {0}_{1} /{2}/ contained containedin={0}'.format(
                    self.syntax_name, syn['name'], syn['re']))
            self.vim.command(
                'highlight default link {}_{} {}'.format(
                    self.syntax_name, syn['name'], syn['link']))

    def gather_candidates(self, context):
        root_dir = self.vim.call('procon#root_dir')

        atcoder = AtCoder(root_dir)
        atcoder.update()

        contests = atcoder.contests

        return list(map(lambda x: self.calc_candidate(x), contests))

    def calc_candidate(self, contest):
        name = contest.key()

        time = contest.time()
        time = time[0:len(time)-3]
        word = '[%s] %s (%s)' % (time, contest.key(), contest.name())

        return {'name': name, 'word': word, 'action__path': contest.root_dir()}
