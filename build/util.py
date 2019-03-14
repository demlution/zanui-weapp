import inspect
import os
import re
import sys

from bs4 import BeautifulSoup as bs4


class F():
    """ file proxy wrapper """
    def __init__(self, path, name=None, mode='t'):
        if name is not None:
            path = os.path.join(path, name)
        self.path = path
        self.mode = mode  # t/b

    @property
    def exists(self):
        return os.path.exists(self.path)

    @property
    def isdir(self):
        return os.path.isdir(self.path)

    @property
    def content(self):
        with open(self.path, f'r{self.mode}') as f:
            return f.read()

    def write(self, content):
        with open(self.path, f'w{self.mode}') as f:
            f.write(content)
        return self

    def unshift(self, content):
        self.write(content + self.content)
        return self

    def append(self, content):
        with open(self.path, f'a{self.mode}') as f:
            f.write(content)
        return self

    def ext(self, _ext):
        if not _ext.startswith('.'):
            _ext = f'.{_ext}'
        path = f'{os.path.splitext(self.path)[0]}{_ext}'
        os.rename(self.path, path)
        self.path = path
        return self

    def rename(self, name):
        path, _ = os.path.split(self.path)
        _, ext = os.path.splitext(self.path)
        if ext:
            name += ext
        path = os.path.join(path, name)
        os.rename(self.path, path)
        self.path = path
        return self

    def rewrite(self, *, content=None, convertor=None):
        if content is None:
            content = self.content
        if convertor is not None:
            content = convertor(content)
        self.write(content)
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
        s = f'<f-ck-xml>{s}</f-ck-xml>'
        soup = bs4(s, 'xml')
        wxses = soup.find_all('wxs')

        def _transform_wxs(wxs):
            wxs.name = 'import-sjs'
            name = wxs['module']
            tag = f'<import-sjs name="{name}" from="../{name}.sjs" />'
            content = '\n'.join(wxs.contents)
            wxs.decompose()
            return (name, tag, content)

        wxses = list(map(_transform_wxs, wxses))

        axml = getattr(soup, 'f-ck-xml').prettify().split('\n')[1:-1]
        axml += [tag for _, tag, _ in wxses]
        axml = '\n'.join(axml)

        sjses = [(name, content) for name, _, content in wxses]

        return axml, sjses

    target = content
    for k, v in REPLACE_MAP.items():
        target = target.replace(k, v)

    ons = []
    catches = []
    pattern = re.compile(r'\s(bind):?(\w+)')
    for m in pattern.finditer(target):
        ons.append(f'on{m.group(2).capitalize()}')
    target = pattern.sub(lambda m: f' on{m.group(2).capitalize()}', target)

    pattern = re.compile(r'\s(catch):?(\w+)')
    for m in pattern.finditer(target):
        catches.append(f'on{m.group(2).capitalize()}')
    target = pattern.sub(lambda m: f' catch{m.group(2).capitalize()}', target)

    return transform_wxs(target)


def catchEvents(content):
    pattern = re.compile(r'\.triggerEvent\(\'(\w+)\'')
    def de_group(match):
        return f'on{match.group(1).capitalize()}'
    return list(map(de_group, pattern.finditer(content)))


def __main__(f):
    locale = inspect.stack()[1][0].f_locals
    module = locale.get("__name__", None)
    if module == '__main__':
        locale[module] = f
        args = sys.argv[1:]
        f(*args)
    return f
