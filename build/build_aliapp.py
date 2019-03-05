#!/usr/bin/python3

import os
import shutil

DIR_BASE = os.path.dirname(__file__)
DIR_DIST = os.path.join(DIR_BASE, 'dist')
DIR_PLUGINS = os.path.abspath('../../bazaar4/dwapp/defaultaliapp/pages')  # FIXME: @sy

# NOTE: 非 entry js 文件无法调用 Component/Page 构造函数
# TESTME: @sy /pages 里面是否能调用 Component 构造函数
# TESTME: @sy 是否能对 Component 构造函数进行重载
# TESTME: @sy fake factory 是否会被调用


class F():
    def __init__(self, path):
        self.path = path

    @property
    def exists(self):
        return os.path.exists(self.path)

    def read(self):
        with open(self.path, 'r') as f:
            return f.read()

    def write(self, content):
        with open(self.path, 'w') as f:
            f.write(content)

    def unshift(self, content):
        _content = cls.read(self.path)
        cls.write(self.path, content + _content)


def get_plugin_name(name):
    return 'plugin-comz' + name.replace('-', '')


def transform_target_dir(target_dir):
    """
    index.js => index.js
    """
    package_js = os.path.join(target_dir, 'package.js')
    f = F(package_js)
    if not f.exists:
        f.write('export default {}\n')


def transform_js(filename, path):
    """
    wx://form-field TODO: @sy polyfill
    """
    behavior_factory = """
var WAComponent = require('../components/shared/wacomponent.js');
var Behavior = WAComponent(function Behavior (x) { return x });
"""
    component_factory = """
var WAComponent = require('../components/shared/wacomponent.js');
Component = WAComponent(Component);
"""
    factory = component_factory if filename == 'index.js' else behavior_factory

    f = F(path)
    code = f.read()
    behavior_polyfill_map = {
        '"wx://form-field"': 'waPolyfillFormField',
        "'wx://form-field'": 'waPolyfillFormField'
    }
    polyfills = ''
    for builtin_behavior in behavior_polyfill_map:
        if builtin_behavior in code:
            polyfill = behavior_polyfill_map[builtin_behavior]
            code.replace(builtin_behavior, polyfill)
            polyfills += f"var {polyfill} = require('../components/shared/{polyfill}.js');\n"

    f.write(factory + polyfills + code)


def pkg_exists(pkg_name):
    return os.path.isdir(os.path.join(DIR_DIST, pkg_name))


def convert_package():
    # packages = filter(pkg_exists, os.listdir(DIR_DIST))  # TODO: @sy
    packages = ['badge-group']
    for package in packages:
        plugin_name = get_plugin_name(package)
        print(f'{package} -> {plugin_name}')
        source_dir = os.path.join(DIR_DIST, package)
        target_dir = os.path.join(DIR_PLUGINS, plugin_name)
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir)
        shutil.copytree(source_dir, target_dir)
        transform_target_dir(target_dir)


def main():
    convert_package()


if __name__ == '__main__':
    main()
