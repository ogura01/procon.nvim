# ============================================================================
# FILE: contest.py
# AUTHOR: ogura <ogura.nop@gmail.com>
# License: MIT license
# ============================================================================

import re
import os

from denite.kind.directory import Kind as Directory
from denite import util

class Kind(Directory):
    def __init__(self, nvim):
        super().__init__(nvim)

        self.nvim = nvim
        self.name = 'contest'
        self.default_action = 'join'

    def echom(self, args):
        self.nvim.command('echom "[Kind][Contest] {}"'.format(args))

    def action_join(self, context):
        for target in context['targets']:
            self.nvim.call('ProJoinContest', target['name'])
