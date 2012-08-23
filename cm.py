#!/usr/bin/env python
import webbrowser
import os
import configparser

import web

import config
import settings
import routine

urls = (
  '/', 'Main',
  '/routine/(.+)', 'routine.PassInfo',
  '/routine', 'routine.Routine',
  '/settings', 'settings.Settings')

global selected_routine
selected_routine = None

app = web.application(urls, globals())
render = web.template.render('templates/')

# Gather routines

def parse_dict(init, lkey):
    '''
    Code by Pavan Kumar Yalamanchili,
    http://stackoverflow.com/a/6027703/622408
    '''
    ret = {}
    for rkey, val in init.items():
        key = lkey + rkey
        if type(val) is dict:
            ret.update(parse_dict(val, key + '/'))
        else:
            ret[key] = val
    return ret

def get_directory_structure(rootdir):
    '''
    Creates a nested dictionary that represents the folder structure of rootdir

    Code by Andrew Clark, licensed under the MIT license,
    http://code.activestate.com/recipes/577879-create-a-nested-dictionary-from-oswalk/
    '''
    dir = {}
    rootdir = rootdir.rstrip(os.sep)
    start = rootdir.rfind(os.sep) + 1
    for path, dirs, files in os.walk(rootdir):
        folders = path[start:].split(os.sep)
        subdir = dict.fromkeys(files)
        parent = reduce(dict.get, folders[:-1], dir)
        parent[folders[-1]] = subdir
    return dir

routines = list(parse_dict(get_directory_structure('./static/data/routines/'), ''))

descs = {}

for each_routine in routines:
    try:
        config = configparser.ConfigParser()
        config.read_string(unicode(open('./static/data/%s' % each_routine, 'r').read()))
        descs[each_routine] = config['General']['title']
    except:
        descs[each_routine] = each_routine.split('/')[-1]

print descs

class Main:
    def GET(self):
        dropdown = web.form.Dropdown('routines', descs.items())
        return render.cm('', '', web.form.Form(dropdown, web.form.Button('Go')))
    def POST(self):
        global selected_routine
        selected_routine = web.input()['routines'][9:]
        web.seeother('/routine/%s' % selected_routine)

if __name__ == "__main__":
    webbrowser.open('http://0.0.0.0:8080/')
    app.run()
