# coding: utf-8

import traceback

import os
import sys
import json
import glob

import functools
import subprocess

if not os.path.dirname(__file__) in sys.path:
    sys.path.append(os.path.dirname(__file__))

from api import API


# ==============================================================================
#
# SampleCase
#
# ==============================================================================
class SampleCase(object):
    def __init__(self, problem, params):
        self.problem = problem
        self.params = params

    def index(self):
        return int(self.params['index'])

    def input_data(self):
        return self.params['input']

    def output_data(self):
        return self.params['output']

    def input_file_path(self):
        return self.input_file_path_static(self.problem, self.index())

    def output_file_path(self):
        return self.output_file_path_static(self.problem, self.index())

    def runner_file_path(self):
        directory = self.problem.contest.tmp_dir()

        problem_key = self.problem.problem_key()
        filename = '%s.%s.txt' % (problem_key, str(self.index()))

        return '%s/%s' % (directory, filename)

    def inspect(self):
        contest_key = self.problem.contest_key()
        problem_key = self.problem.problem_key()
        index = str(self.params['index'])

        return 'SampleCase(%s/%s/%s)' % (contest_key, problem_key, index)

    def __repr__(self):
        return self.inspect()

    def save(self):
        input_file_path = self.input_file_path()
        output_file_path = self.output_file_path()

        try:
            print('Write: %s' % input_file_path)
            os.makedirs(os.path.dirname(input_file_path), exist_ok=True)
            with open(input_file_path, mode='w') as f:
                f.write(self.input_data())
                f.write("\n")

            print('Write: %s' % output_file_path)
            os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
            with open(output_file_path, mode='w') as f:
                f.write(self.output_data())
                f.write("\n")
        except Exception as exception:
            print(exception)
            traceback.print_exc()

    def read_results(self):
        return {
            'input': self.read_file_safely(self.input_file_path()),
            'output': self.read_file_safely(self.output_file_path()),
            'runner': self.read_file_safely(self.runner_file_path())
            }

    def read_file_safely(self, file_path):
        try:
            with open(file_path) as f:
                return f.read().strip()
        except Exception as exception:
            print(exception)
            traceback.print_exc()

        return ''

    def diff(self):
        lhs = self.runner_file_path()
        rhs = self.output_file_path()
        process = subprocess.run(['diff', lhs, rhs], stdout=subprocess.DEVNULL)
        return process.returncode == 0

    @classmethod
    def base_dir(self, problem):
        return '%s/samples' % problem.contest.root_dir()

    @classmethod
    def input_file_path_static(self, problem, index):
        directory = self.base_dir(problem)
        return '%s/%s.%d.in' % (directory, problem.problem_key(), index)

    @classmethod
    def output_file_path_static(self, problem, index):
        directory = self.base_dir(problem)
        return '%s/%s.%d.out' % (directory, problem.problem_key(), index)

    @classmethod
    def glob_input_files(self, problem):
        directory = self.base_dir(problem)
        return glob.glob('%s/%s.*.in' % (directory, problem.problem_key()))

    @classmethod
    def glob_output_files(self, problem):
        directory = self.base_dir(problem)
        return glob.glob('%s/%s.*.out' % (directory, problem.problem_key()))

    @classmethod
    def load(self, problem, index):
        input_file_path = self.input_file_path_static(problem, index)
        output_file_path = self.output_file_path_static(problem, index)

        if not(os.path.exists(input_file_path)):
            return None

        if not(os.path.exists(output_file_path)):
            return None

        params = {'index': index}

        try:
            with open(input_file_path, mode='r') as f:
                params['input'] = f.read()

            with open(output_file_path, mode='r') as f:
                params['output'] = f.read()

            return SampleCase(problem, params)
        except Exception as exception:
            print(exception)
            traceback.print_exc()

        return None

    @classmethod
    def create_sample_cases_from_website(self, problem):
        contest_key = problem.contest_key()
        problem_key = problem.problem_key()
        params_list = problem.api().get_sample_cases(contest_key, problem_key)
        return [SampleCase(problem, params) for params in params_list]


# ==============================================================================
#
# code
#
# ==============================================================================
class Code(object):
    def __init__(self, problem, params):
        self.problem = problem
        self.params = {}

    def source_path(self):
        contest_dir = self.problem.contest.root_dir()
        return '%s/%s.cpp' % (contest_dir, self.problem.problem_key())

    def binary_path(self):
        tmpdir = self.problem.contest.tmp_dir()
        return '%s/%s.out' % (tmpdir, self.problem.problem_key())

    def __repr__(self):
        source_path = self.source_path()
        dirname = os.path.basename(os.path.dirname(source_path))
        basename = os.path.basename(source_path)
        return 'Code({}: {})'.format(dirname, basename)

    def update(self):
        source_path = self.source_path()

        if not os.path.exists(source_path):
            with open(source_path, mode='w') as f:
                f.write('')


# ==============================================================================
#
# Problem
#
# ==============================================================================
class Problem(object):
    def __init__(self, contest, params):
        self.contest = contest
        self.params = params

        self.sample_cases = []
        self.code = Code(self, {})

    def api(self):
        return self.contest.api()

    def contest_key(self):
        return self.contest.key()

    def problem_key(self):
        return self.params['key']

    def name(self):
        return self.params['name']

    def score(self):
        if 'score' in self.params:
            return self.params['score']
        return None

    def inspect(self):
        contest_key = self.contest_key()
        problem_key = self.problem_key()
        key = '%s_%s' % (contest_key, problem_key)
        return 'Problem(%s: %s - %s)' % (key, self.name(), self.score())

    def __repr__(self):
        return self.inspect()

    def update(self, is_force=False):
        self.code.update()
        self.update_sample_case()

    def update_info_and_sample_cases(self):
        contest_key = self.contest_key()
        problem_key = self.problem_key()

        api = self.api()
        res = api.get_problem_info_and_sample_cases(contest_key, problem_key)

        self.params.update(res['info'])
        self.sample_cases = res['sample_cases']

    def update_sample_case(self, is_force=False):
        self.sample_cases = self.load_sample_case_from_cache()

        if is_force or len(self.sample_cases) == 0:
            self.sample_cases = self.update_from_website()

    def update_from_website(self):
        sample_cases = SampleCase.create_sample_cases_from_website(self)

        for sample_case in sample_cases:
            sample_case.save()

        return sample_cases

    def load_sample_case_from_cache(self):
        input_files = SampleCase.glob_input_files(self)
        output_files = SampleCase.glob_output_files(self)

        length = max(len(input_files), len(output_files))
        indexes = range(1, length + 1)

        sample_cases = [SampleCase.load(self, index) for index in indexes]
        return list(filter(lambda x: x, sample_cases))

    @classmethod
    def create_problems_from_website(self, contest):
        params_list = contest.api().get_problem_params_list(contest.key())
        problems = [Problem(contest, params) for params in params_list]

        for problem in problems:
            problem.update_info_and_sample_cases()

        return problems


# ==============================================================================
#
# Contest
#
# ==============================================================================
class Contest(object):
    def __init__(self, atcoder, params):
        self.atcoder = atcoder
        self.params = params

        self.problems = []
        self.sample_cases = []

    def api(self):
        return self.atcoder.api

    def key(self):
        return self.params['key']

    def name(self):
        return self.params['name']

    def time(self):
        return self.params['time']

    def root_dir(self):
        return '%s/%s' % (self.atcoder.root_dir(), self.key())

    def tmp_dir(self):
        return '%s/tmp' % self.root_dir()

    def problem_list_path(self):
        return '%s/problems.json' % self.root_dir()

    def inspect(self):
        return 'Contest(%s)' % self.key()

    def __repr__(self):
        return self.inspect()

    def load(self):
        self.problems = self.load_problems_from_cache()
        self.problems = sorted(self.problems, key=lambda x: x.contest_key())

    def update(self, is_force=False):
        if is_force or len(self.problems) == 0:
            self.problems = self.update_problems_from_website()
            self.save()
        else:
            self.load()

        for problem in self.problems:
            print(problem.inspect())
            problem.update()

    def update_problems_from_website(self):
        return Problem.create_problems_from_website(self)

    def save(self):
        json_data = json.dumps([problem.params for problem in self.problems])

        try:
            os.makedirs(self.root_dir(), exist_ok=True)
            with open(self.problem_list_path(), mode='w') as f:
                f.write(json_data)
        except Exception as exception:
            print(exception)
            traceback.print_exc()

    def load_problems_from_cache(self):
        if not os.path.exists(self.problem_list_path()):
            return []

        problem_params_list = []
        try:
            with open(self.problem_list_path(), mode='r') as f:
                problem_params_list = json.load(f)
        except Exception as exception:
            print(exception)
            traceback.print_exc()

        return [Problem(self, params) for params in problem_params_list]

    def find_problem(self, key):
        compare = (lambda x: x.problem_key() == key)
        problems = list(filter(compare, self.problems))

        return problems[0] if len(problems) != 0 else None


# ==============================================================================
#
# AtCoder
#
# ==============================================================================
class AtCoder(object):
    def __init__(self, root_dir, params={}):
        self.api = API()
        self._root_dir = root_dir
        self.contests = []

    def find_contest(self, key):
        contests = list(filter(lambda x: x.key() == key, self.contests))
        return contests[0] if len(contests) != 0 else None

    def find_or_create_contest(self, key):
        contest = self.find_contest(key)
        return contest if contest else Contest(self, {'key': key})

    def root_dir(self):
        return self._root_dir

    def contests_cache_path(self):
        return '%s/contests.json' % self.root_dir()

    def set_root_dir(self, root_dir):
        self._root_dir = root_dir

    def problems(self):
        problems_list = map(lambda contest: contest.problems, self.contests)
        return functools.reduce(lambda a, b: a + b, problems_list)

    def load(self):
        self.contests = self.load_contests_from_cache()

        sorter = (lambda x: x.time())
        self.contests = sorted(self.contests, key=sorter, reverse=True)

        for contest in self.contests:
            contest.load()

        return self

    def update(self, is_force=False, index=0):
        self.load()

        if is_force or len(self.contests) == 0:
            self.contests = self.update_contests_from_website(index)

        for contest in self.contests:
            print(contest.inspect())

    def load_contests_from_cache(self):
        try:
            if os.path.exists(self.contests_cache_path()):
                with open(self.contests_cache_path(), mode='r') as f:
                    parameterSet = json.load(f)
                    return [Contest(self, params) for params in parameterSet]
        except Exception as exception:
            print(exception)
            traceback.print_exc()

        return []

    def load_cache_from_website(self, is_force=False, index=0):
        params_list = self.api.get_contest_params_list(index)
        return [Contest(self, params) for params in params_list]

    def update_contests_from_website(self, index):
        contests = self.load_cache_from_website(index)

        sorter = (lambda x: x.time())
        contests = sorted(contests, key=sorter, reverse=True)
        json_data = json.dumps([contest.params for contest in contests])

        cache_path = self.contests_cache_path()

        try:
            os.makedirs(os.path.dirname(cache_path), exist_ok=True)
            print('write ' + cache_path)
            with open(cache_path, mode='w') as f:
                f.write(json_data)
        except Exception as exception:
            print(exception)
            traceback.print_exc()

        return contests


if __name__ == '__main__':
    root_dir = os.path.expandvars('$HOME/.procon/atcoder')
    atcoder = AtCoder(root_dir)
    # atcoder.load()
