#!/usr/bin/python3

import os
import shutil

from util import F, __main__, dxml2axml

# DIR_BASE = os.path.dirname(__file__)
DIR_DIST = os.path.abspath('dist')
DIR_PLUGINS = os.path.abspath('../bazaar4/dwapp/defaultaliapp/pages')  # FIXME: @sy

# NOTE: 非 entry js 文件无法调用 Component/Page 构造函数

__doc__ = """
字面量的处理在这个脚本进行，把 vant 文件搬到 bazzar4/dwapp
逻辑相关在 defaultapp 里面通过 factory proxy 即 WAComponent 在运行时兼容处理
其中 Behavior 也是用 WAComponent 套函数转换的
"""


def get_plugin_name(name):
    return 'plugin-comz' + name.replace('-', '')


def transform_target_dir(target_dir):
    names = os.listdir(target_dir)
    for name in names:
        if name.endswith('.js'):
            transform_js(target_dir, name)
        elif name.endswith('.wxml'):
            transform_html(target_dir, name)
        elif name.endswith('.wxss'):
            transform_css(target_dir, name)


def transform_js(path, filename):
    """
    wx://form-field TODO: @sy polyfill
    """
    behavior_factory = """
var WAComponent = require('../../components/shared/wacomponent.js');
var Behavior = WAComponent(function Behavior (x) { return x });
"""
    component_factory = """
var WAComponent = require('../../components/shared/wacomponent.js');
Component = WAComponent(Component);
"""
    factory = component_factory if filename == 'index.js' else behavior_factory

    f = F(path, filename)
    use_strict = "'use strict';"
    code = f.read().replace(use_strict, '')
    behavior_polyfill_map = {
        '"wx://form-field"': 'formField',
        "'wx://form-field'": 'formField'
    }
    polyfills = ''
    for builtin_behavior in behavior_polyfill_map:
        if builtin_behavior in code:
            polyfill = f"waPolyfill{behavior_polyfill_map[builtin_behavior].capitalize()}"
            code.replace(builtin_behavior, polyfill)
            polyfills += f"var {polyfill} = require('../components/shared/wa-polyfill-{polyfill.lower()}.js');\n"

    f.write(use_strict + factory + polyfills + code)


def transform_html(path, filename):
    F(path, filename).rewrite(convertor=dxml2axml).ext('axml')


def transform_css(path, filename):
    F(path, filename).ext('acss')


def pkg_exists(pkg_name):
    # TODO: @sy common 特殊处理
    return F(DIR_DIST, pkg_name).isdir


@__main__
def convert_package():
    packages = filter(pkg_exists, os.listdir(DIR_DIST))  # TODO: @sy 有些暂时不能支持
    for package in packages:
        plugin_name = get_plugin_name(package)
        print('{:16} ->  {:16}'.format(package, plugin_name))
        source_dir = os.path.join(DIR_DIST, package)
        target_dir = os.path.join(DIR_PLUGINS, plugin_name)
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir)
        shutil.copytree(source_dir, target_dir)
        transform_target_dir(target_dir)
