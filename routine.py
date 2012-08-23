#!/usr/bin/env python
import time
import configparser
import sys

import web

render = web.template.render('templates/')

selected_routine = None
next_block = ''
current_block = ''
config = None

class PassInfo:
    '''Hackish way to get routine name; there may be a better way to do this'''
    def GET(self, routine):
        global config
        global current_block
        config = configparser.ConfigParser()
        config.read_string(unicode(open('./static/data/routines/%s' % routine, 'r').read()))
         
        if 'General' not in config.keys():
            raise LookupError, 'No "General" block defined in routine %s.' % routine
        if ('end' not in config['General']) or ('start' not in config['General']):
            raise LookupError, 'No "start" or "end" options defined in "General" block in routine %s' % routine

        first = config['General']['start']
        last = config['General']['end']

        current_block = first
        next_block = ''
        web.seeother('/routine')

class Routine:
    '''Handles routine runtime.
    TODO: Fix messy block transition system'''

    def process(self, block):
        global config
        text = config[block]['message'] if 'askyn' not in config[block] else config[block]['askyn'].split('|')[0]
        text = web.websafe(text).replace('\\n', '<br>')
        try:
            picture = config[block]['picture']
        except KeyError:
            picture = ''
        buttons = []
        if 'askyn' in config[block]:
            delay_type = 'askyn'
            for index, button in enumerate(config[block]['askyn'].split('|')[1:]):
                buttons.append(web.form.Button(name='choice', value=config[block][['yes', 'no'][index]], html=button))
        else:
            if 'delay' in config[block]:
                if config[block]['delay'].split('|')[0] == 'button':
                    delay_type = 'button'
                    buttons.append(web.form.Button(config[block]['delay'].split('|')[1]))
                else:
                    delay_type = 'time'
                    delay_time = float(config[block]['delay'])
        form = web.form.Form(*buttons)
        return {'text':text, 'picture':picture, 'form':form, 'delay_type':delay_type, 'delay_time':(delay_time if delay_type == 'time' else None)}

    def GET(self):
        print 'GET'
        global next_block
        global current_block
        if next_block:
            print next_block
            info = self.process(next_block)
            current_block = next_block
            next_block = ''
        else:
            info = self.process(current_block)
        if info['delay_type'] == 'time':
            time.sleep(info['delay_time'])
            current_block = info['next']
            info = self.process(current_block)
        return render.cm(info['text'], info['picture'], info['form'])

    def POST(self):
        print 'POST'
        global next_block
        global current_block
        try:
            next_block = str(web.input().choice)
        except AttributeError:
            next_block = config[current_block]['next']
            print current_block
        web.seeother('/routine')
