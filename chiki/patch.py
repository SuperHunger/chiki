# coding: utf-8
import flask
import string
import random
from flask import Flask, url_for, current_app
from flask.app import setupmethod
from functools import wraps

case = string.lowercase + string.digits
old_add_url_rule = Flask.add_url_rule
old_url_for = url_for
funcs = dict()


def url_for(endpoint, **values):
    if current_app.config.get('PATCH_URL'):
        arg1 = ''.join(random.sample(case, random.randint(2, 4)))
        arg2 = ''.join(random.sample(case, random.randint(2, 4)))
        return old_url_for(endpoint, _arg1=arg1, _arg2=arg2, **values)
    return old_url_for(endpoint, **values)


@setupmethod
def add_url_rule(self, rule, endpoint=None, view_func=None, **options):
    rule2 = '/<_arg1>-1/' + rule[1:]
    if rule2.endswith('/'):
        rule2 += '<_arg2>.html'
    else:
        rule2 += '/<_arg2>.html'

    func = view_func
    if self.config.get('PATCH_URL') and func:
        func = funcs.get(func, None)
        if not func:
            @wraps(view_func)
            def func(*args, **kwargs):
                if '_arg1' in kwargs:
                    kwargs.pop('_arg1')
                if '_arg2' in kwargs:
                    kwargs.pop('_arg2')
                return view_func(*args, **kwargs)
        funcs[view_func] = func

    old_add_url_rule(self, rule, endpoint=endpoint,
                     view_func=func, **options)
    options.setdefault('defaults', {'_arg1': '', '_arg2': ''})
    return old_add_url_rule(self, rule2, endpoint=endpoint,
                            view_func=func, **options)


def patch_url():
    Flask.add_url_rule = add_url_rule
    flask.url_for = url_for
