# coding: utf-8

from atcoder import AtCoder, Contest, Problem

import os
import sys
import time
import subprocess

class Runner:
    def __init__(self, source_path):
        self.source_path = source_path

    def load(self):
        contest_dir = os.path.dirname(self.source_path)
        root_dir    = os.path.dirname(contest_dir)

        contest_key = os.path.basename(contest_dir)
        problem_key = os.path.splitext(os.path.basename(self.source_path))[0]

        atcoder = AtCoder(root_dir).load()
        contest = atcoder.find_contest(contest_key) or Contest(atcoder, { 'key': contest_key })
        contest.load()

        problem = contest.find_problem(problem_key)
        problem.update()

        return problem

    def execute(self, test_index):
        problem = self.load()
        self.compile(self.source_path, problem.code.binary_path())

        sample_cases = problem.sample_cases

        if test_index != -1:
            sample_cases = list(filter(lambda x: x.index() == test_index, sample_cases))

        if len(sample_cases) == 0:
            print('no sample_cases by index({})'.format(test_index))
            return

        print('======================================')

        self.testrun(sample_cases)
        self.show_results(sample_cases)

    def compile(self, source_path, binary_path):
        command = ['g++', source_path, '-o', binary_path]
        # print('>> {}'.format(' '.join(command)), flush = True)

        os.makedirs(os.path.dirname(binary_path), exist_ok = True)
        return subprocess.run(command, stdout=subprocess.PIPE, check=True)

    def testrun(self, sample_cases):
        for sample_case in sample_cases:
            self.testrun_impl(sample_case)

    def testrun_impl(self, sample_case):
        print('{}: '.format(sample_case), end='', flush = True)
        try:
            elapsed_time = self.execute_command(sample_case)
            status = 'AC' if sample_case.diff() else 'WA'
            status = status if elapsed_time <= 2.0 else 'TLE'
            print('{} ... {:.02f}s'.format(status, elapsed_time))
        except Exception as exception:
            print(exception)
            print(sys.exc_info())

    def execute_command(self, sample_case):
        binary_path = sample_case.problem.code.binary_path()
        input_file_path  = sample_case.input_file_path()
        runner_file_path = sample_case.runner_file_path()

        command = 'time %s <%s >%s' % (binary_path, input_file_path, runner_file_path)

        t1 = time.time()
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        t2 = time.time()

        return t2 - t1

    def show_results(self, sample_cases):
        for sample_case in sample_cases:
            res = sample_case.read_results()

            print('--------------------------------------')
            print('--- sample input  (%s) ---' % str(sample_case.index()))
            print(res['input'])
            print('--- sample output (%s) ---' % str(sample_case.index()))
            print(res['output'])
            print('--- runner output (%s) ---' % str(sample_case.index()))
            print(res['runner'])

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        raise Exception('please, input source_path argment!')

    source_path = sys.argv[1]

    if not(os.path.exists(source_path)):
        raise Exception('not found: %s' % source_path)

    test_index = -1
    if len(sys.argv) >= 2:
        test_index = int(sys.argv[2])

    runner = Runner(source_path)
    runner.execute(test_index)
