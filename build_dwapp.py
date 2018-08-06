# coding: utf-8

import os
import shutil

DIR_BASE = os.path.dirname(__file__)
DIR_DIST = os.path.join(DIR_BASE, 'dist')
DIR_PLUGINS = os.path.abspath('../bazaar4/dwapp/defaultapp/pages')


def get_plugin_name(name):
    return 'plugin-comz' + name.replace('-', '')


def transform_target_dir(target_dir):
    package_js = os.path.join(target_dir, 'package.js')
    if not os.path.exists(package_js):
        with open(package_js, 'w') as f:
            f.write('export default {}\n')


def convert_package():
    packages = [i for i in os.listdir(DIR_DIST) if os.path.isdir(os.path.join(DIR_DIST, i))]
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
