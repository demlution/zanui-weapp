/**
 * @file
 * 先编译到ali小程序以后再跑这个脚本
 * 会编译出 props 和 events 在 node_modules/@doc/<组件名>.doc.html
 */
/* eslint-disable no-await-in-loop */
/* eslint-disable space-before-function-paren */
/* eslint-disable semi, global-require, import/no-dynamic-require, arrow-parens, prefer-destructuring */

const fs = require('fs')
const path = require('path')
const { promisify } = require('util')

const readFile = promisify(fs.readFile)
const readdir = promisify(fs.readdir)
const writeFile = promisify(fs.writeFile)
const exists = promisify(fs.exists)

const DIST = path.resolve(__dirname, '../dist')
const BUILT = path.resolve(__dirname, '../../bazaar4/dwapp/defaultaliapp/pages')
const TARGET = path.resolve(__dirname, '../node_modules/@doc')

async function asyncForEach (array, callback) {
  for (let index = 0; index < array.length; index++) {
    await callback(array[index], index, array)
  }
}

async function main () {
  const packages = await readdir(DIST)
  const td = v => `<td>${v === undefined ? '' : v}</td>`
  // console.log(packages)
  Number.toString = () => 'Number'
  String.toString = () => 'String'
  Function.toString = () => 'Function'
  Boolean.toString = () => 'Boolean'
  Array.toString = () => 'Array'
  const __undefined = {}
  __undefined.toString = () => 'undefined'
  const types = [
    'Number', 'String', 'Function', 'Boolean', 'Array', 'undefined'
  ]

  let currentComponent

  global.Component = (options => {
    currentComponent = ''
    Object.keys(options.properties || {}).forEach(key => {
      const prop = options.properties[key]
      let type = (prop.type || __undefined).toString()
      let value = prop.value === undefined ? prop.toString() : prop.value
      if (type === 'undefined' && types.includes(value)) {
        type = value
        value = 'undefined'
      }
      type = String(type)
      value = String(value)
      if (type === undefined || type === 'undefined') {
        type === '?'
      }
      if (value === undefined || value === '[object Object]') {
        value = ''
      }
      currentComponent += `<tr>${td(key)}${td(type)}${td(value)}</tr>\n`
    })
  })
  global.Behavior = Component

  asyncForEach(packages, async pkg => {
    const file = path.resolve(DIST, pkg, 'index.js')
    if (!(await exists(file))) return
    await require(file)

    const event = path.resolve(BUILT, `plugin-comz${pkg}`, 'wa-polyfill-runtime-event.js')
    if (await exists(event)) {
      const deCapitalize = s => s.trim().replace(/on([A-Z])/, (match, p1) => p1.toLowerCase())
      const events = (await readFile(event, 'utf8'))
        .split('\n')
        .filter(line => line.startsWith('    '))
        .map(line => deCapitalize(line.split(':')[0]))
        .map(event => `<tr>${td(event)}${td()}${td('-')}</tr>`)
      currentComponent += '\n' + events.join('\n')
    }

    const doc = path.resolve(TARGET, `${pkg}.doc.html`)
    await writeFile(doc, currentComponent)
  })
}

fs.rmdir(TARGET, () => fs.mkdir(TARGET, main))
