#!/usr/bin/python3

import os
import shutil

from util import F, __main__, dxml2axml, catchEvents


__doc__ = """
字面量的处理在这个脚本进行，把 vant 文件搬到 bazzar4/dwapp
逻辑相关在 defaultapp 里面通过 factory proxy 即 WAComponent 在运行时兼容处理
其中 Behavior 也是用 WAComponent 套函数转换的

为了保持大小写 html 用 bs4 当 xml 读，支付宝小程序支持 <slot/> 这样的写法
事件都会在读 html 以后写入单独的 js 文件在运行时当做 props 传入

NOTE: 非 entry js 文件无法调用 Component/Page 构造函数
"""


# DIR_BASE = os.path.dirname(__file__)
DIR_DIST = os.path.abspath('dist')
DIR_PLUGINS = os.path.abspath('../bazaar4/dwapp/defaultaliapp/pages')  # FIXME: @sy


def get_plugin_name(name):
    return 'plugin-comz' + name.replace('-', '')


def transform_target_dir(target_dir, depth=2):
    names = os.listdir(target_dir)
    ons = []
    root = '../' * depth
    for name in names:
        if name.endswith('.js'):
            transform_js(target_dir, name, root)
            ons += catchEvents(F(target_dir, name).content)
        elif name.endswith('.wxml'):
            transform_html(target_dir, name)
        elif name.endswith('.wxss'):
            transform_css(target_dir, name)
        elif name.endswith('.json'):
            continue
        elif F(target_dir, name).isdir:
            transform_target_dir(os.path.join(target_dir, name), depth + 1)

    ons = list(set(ons))

    event_polyfill = f"""'use strict';
var WAComponent = require('{root}components/shared/wacomponent.js');
var Behavior = WAComponent(function Behavior (x) {{ return x }});

module.exports = Behavior({{}});
"""
    events = ''
    for on in ons:
        events += f'    {on}: function () {{}},\n'
    if events:
        events = '\n'.join(filter(bool, events.split('\n')))
        event_polyfill = f"""'use strict';
var WAComponent = require('{root}components/shared/wacomponent.js');
var Behavior = WAComponent(function Behavior (x) {{ return x }});

module.exports = Behavior({{
  properties: {{
{events}
  }}
}});
"""
    F(target_dir, 'wa-polyfill-runtime-event.js').write(event_polyfill)


def transform_js(path, filename, root):
    behavior_factory = f"""
var WAComponent = require('{root}components/shared/wacomponent.js');
var Behavior = WAComponent(function Behavior (x) {{ return x }});
"""
    component_factory = f"""
var WAComponent = require('{root}components/shared/wacomponent.js');
var triggerPolyfill = require('{root}components/shared/wa-polyfill-trigger.js');
var eventPolyfill = require('./wa-polyfill-runtime-event.js');
Component = WAComponent(Component, [triggerPolyfill, eventPolyfill]);
"""
    factory = component_factory if filename == 'index.js' else behavior_factory

    f = F(path, filename)
    use_strict = "'use strict';"
    code = f.content.replace(use_strict, '')
    behavior_polyfill_map = {
        '"wx://form-field"': 'formField',
        "'wx://form-field'": 'formField'
    }
    polyfills = ''
    for builtin_behavior in behavior_polyfill_map:
        if builtin_behavior in code:
            polyfill = f"waPolyfill{behavior_polyfill_map[builtin_behavior].capitalize()}"
            code.replace(builtin_behavior, polyfill)
            polyfills += f"var {polyfill} = require('{root}components/shared/wa-polyfill-{polyfill.lower()}.js');\n"

    f.write(use_strict + factory + polyfills + code)


def transform_html(path, filename):
    f = F(path, filename)
    axml, sjses = dxml2axml(f.content)
    f.write(axml).ext('axml')
    for name, content in sjses:
        F(path, f'{name}.sjs').write(content)


def transform_css(path, filename):
    F(path, filename).ext('acss')


def pkg_exists(pkg_name):
    return F(DIR_DIST, pkg_name).isdir


def worker(package):
    plugin_name = get_plugin_name(package)
    print('{:16} ->  {:16}'.format(package, plugin_name))
    source_dir = os.path.join(DIR_DIST, package)
    target_dir = os.path.join(DIR_PLUGINS, plugin_name)
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
    shutil.copytree(source_dir, target_dir)
    transform_target_dir(target_dir)


@__main__
def convert_package():
    list(map(worker, filter(pkg_exists, os.listdir(DIR_DIST))))
