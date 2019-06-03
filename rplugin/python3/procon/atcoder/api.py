# coding: utf-8

import traceback

import urllib.parse
import urllib.request

import os
import re
import random
import time

CONTEST_PATTERN = r'(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d).*?<a href=\'/contests/([^\']+)\'>([^<]+)</a>' # noqa
INPUT_PATTERN = r'<h3>Sample Input ([0-9]+)</h3><pre>(.+?)</pre>'
OUTPUT_PATTERN = r'<h3>Sample Output ([0-9]+)</h3><pre>(.+?)</pre>'


# ==============================================================================
#
# API
#
# ==============================================================================
class API(object):
    def __init__(self):
        self.base_url = 'https://atcoder.jp'

        option = re.MULTILINE | re.DOTALL
        self.contest_list_pattern = re.compile(CONTEST_PATTERN, option)
        self.sample_input_pattern = re.compile(INPUT_PATTERN, option)
        self.sample_output_pattern = re.compile(OUTPUT_PATTERN, option)

        self.problem_score_pattern = re.compile(r'<p>.*?配点.*?(\d+).*?</p>')

        self.accessing_count = 0
        self.sleeping_count = 1

    def open(self, url):
        self.sleep_random()
        print('open >> ' + url, flush=True)
        req = urllib.request.Request(url)
        return urllib.request.urlopen(req)

    def sleep_random(self):
        self.accessing_count += 1

        if self.accessing_count <= self.sleeping_count:
            return

        sleeping_time_span = 1.0 + random.random()
        # print('Sleep: %s' % str(sleeping_time_span))

        time.sleep(sleeping_time_span)
        self.sleeping_count = self.sleeping_count + 1

    def read(self, body_binary):
        body = body_binary.decode('utf-8').replace("\r", '')
        lines = map(lambda x: x.strip(), body.split("\n"))
        return "\n".join(filter(lambda x: x, lines))

    def get_contest_params_list(self, page=0):
        postfix = '/archive?page=' + str(page) if page != 0 else ''
        url = self.base_url + '/contests' + postfix

        params_list = []
        try:
            with self.open(url) as res:
                body = self.read(res.read())
                params_list = self.parse_html_to_contest_params_list(body)
        except Exception as exception:
            print(exception)
            traceback.print_exc()

        return params_list

    def parse_html_to_contest_params_list(self, body):
        pattern = self.contest_list_pattern
        matches = [matched for matched in pattern.finditer(body)]

        params_list = [
                {
                  'time': matched.group(1),
                  'key':  matched.group(2),
                  'name': matched.group(3)
                }
                for matched in matches
            ]

        params_list = filter(lambda x: 'archive' not in x['key'], params_list)
        params_list = filter(lambda x: 'practice' not in x['key'], params_list)
        return params_list

    def get_task_url(self, contest_key):
        return '%s/contests/%s/tasks' % (self.base_url, contest_key)

    def get_problem_params_list(self, contest_key):
        url = self.get_task_url(contest_key)

        key = '/contests/%s/tasks/%s' % (contest_key, contest_key)
        s = '<a href=\'%s_(.+?)\'>(.+?)</a>' % key
        pattern = re.compile(s, re.MULTILINE | re.DOTALL)

        params = {}

        try:
            with self.open(url) as res:
                body = self.read(res.read())
                for matched in pattern.finditer(body):
                    key = matched.group(1).strip()
                    name = matched.group(2).strip()
                    params[key] = name
        except Exception as exception:
            print(exception)
            traceback.print_exc()

        return [{'key': key, 'name': name} for key, name in params.items()]

    def get_sample_cases(self, contest_key, problem_key):
        url = self.get_task_url(contest_key)
        url = '%s/%s_%s' % (url, contest_key, problem_key)

        sample_cases = []

        try:
            with self.open(url) as res:
                body = self.read(res.read())
                sample_cases = self.create_sample_cases(body)
        except Exception as exception:
            print(exception)
            traceback.print_exc()

        return sample_cases

    def create_sample_cases(self, body):
        sample_case_params_dict = {}

        def add(key, matched):
            index = int(matched.group(1).strip())
            data = matched.group(2).strip()

            if index not in sample_case_params_dict:
                sample_case_params_dict[index] = {'index': index}

            sample_case_params_dict[index][key] = data

        for matched in self.sample_input_pattern.finditer(body):
            add('input', matched)

        for matched in self.sample_output_pattern.finditer(body):
            add('output', matched)

        return [params for params in sample_case_params_dict.values()]

    def get_problem_info(self, contest_key, problem_key):
        url = self.get_task_url(contest_key)
        url = '%s/%s_%s' % (url, contest_key, problem_key)

        info = {}

        try:
            with self.open(url) as res:
                info = self.create_problem_info(self.read(res.read()))
        except Exception as exception:
            print(exception)
            traceback.print_exc()

        return info

    def create_problem_info(self, body):
        matched = self.problem_score_pattern.search(body)

        info = {}
        info['score'] = int(matched.group(1))

        return info

    def get_problem_info_and_sample_cases(self, contest_key, problem_key):
        url = self.get_task_url(contest_key)
        url = '%s/%s_%s' % (url, contest_key, problem_key)

        info = {}
        sample_cases = []

        try:
            with self.open(url) as res:
                body = self.read(res.read())

                info = self.create_problem_info(body)
                sample_cases = self.create_sample_cases(body)
        except Exception as exception:
            print(exception)
            traceback.print_exc()

        return {'info': info, 'sample_cases': sample_cases}

    def create_submit_params(self, source_path):
        data = ''
        with open(source_path) as f:
            data = f.read()

        problem_key = os.path.basename(source_path).split('.')[0]
        contest_key = os.path.basename(os.path.dirname(source_path))

        token = self.get_csrf_token(contest_key)

        params = {
            'data.TaskScreenName': ('%s_%s' % (contest_key, problem_key)),
            'data.LanguageId': 3003,
            'sourceCode': data,
            'csrf_token': token
        }

        return params

    def get_csrf_token(self, contest_key):
        pattern = re.compile(r'.*csrf_token.*value=\'(.+)\'.*')

        url = '%s/contests/%s/submit' % (self.base_url, contest_key)
        with self.open(url) as res:
            body = self.read(res.read())
            lines = body.split("\n")

            matches = map(lambda x:  pattern.search(x), lines)
            matches = filter(lambda x: x, matches)

            for matched in matches:
                return matched.group(1)

        raise Exception('ERROR')

    def submit(self, source_path):
        print(source_path)

        contest_dir = os.path.dirname(source_path)
        contest_key = os.path.basename(contest_dir)

        url = '%s/contests/%s/submit' % (self.base_url, contest_key)
        params = self.create_submit_params(source_path)

        print(url, flush=True)
        print(params, flush=True)

        self.sleep_random()
        print('open >> ' + url, flush=True)

        encoded_params = urllib.parse.urlencode(params)
        req = urllib.request.Request('{}?{}'.format(url, encoded_params))
        with urllib.request.urlopen(req) as res:
            body = self.read(res.read())
            print(body)


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    source_path = os.path.expanduser('~/.procon/atcoder/abc128/a.cpp')
    api = API()
    # api.submit(source_path)
