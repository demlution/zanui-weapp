import inspect
import os
import re
import sys

from bs4 import BeautifulSoup as bs4


class F():
    """ file proxy wrapper """
    def __init__(self, path, name=None):
        if name is not None:
            path = os.path.join(path, name)
        self.path = path

    @property
    def exists(self):
        return os.path.exists(self.path)

    @property
    def isdir(self):
        return os.path.isdir(self.path)

    def read(self):
        """ unlinkable """
        with open(self.path, 'r') as f:
            return f.read()

    def write(self, content):
        with open(self.path, 'w') as f:
            f.write(content)
        return self

    def unshift(self, content):
        _content = cls.read(self.path)
        cls.write(self.path, content + _content)
        return self

    def ext(self, _ext):
        if not _ext.startswith('.'):
            _ext = f'.{_ext}'
        path = f'{os.path.splitext(self.path)[0]}{_ext}'
        os.rename(self.path, path)
        return self

    def rewrite(self, *, content=None, convertor=None):
        if content is not None:
            self.write(content)
        elif convertor is not None:
            self.write(convertor(self.read()))
        return self


def dxml2axml(content):
    REPLACE_MAP = {
        'wx:if': 'a:if',
        'wx-if': 'a:if',
        'wx:elif': 'a:elif',
        'wx:else': 'a:else',
        'wx:for': 'a:for',
        'wx:for-item': 'a:for-item',
        'wx:for-index': 'a:for-index',
        'wx:key': 'a:key',
    }

    def transform_wxs(s):
        soup = bs4(s, 'xml')
        wxses = soup.find_all('wxs')
        for wxs in wxses:
            wxs.name = 'import-sjs'
            wxs['name'] = wxs['module']
            wxs['from'] = wxs['src']
            del wxs['module']
            del wxs['src']
        return str(soup.view)

    target = content
    for k, v in REPLACE_MAP.items():
        target = target.replace(k, v)

    re.compile(r'^(bind):?(\w+)').sub(lambda m: f'on{m.group(2).capitalize()}', target)
    re.compile(r'^(catch):?(\w+)').sub(lambda m: f'catch{m.group(2).capitalize()}', target)

    target = transform_wxs(target)

    return target


def __main__(f):
    locale = inspect.stack()[1][0].f_locals
    module = locale.get("__name__", None)
    if module == '__main__':
        locale[module] = f
        args = sys.argv[1:]
        f(*args)
    return f
