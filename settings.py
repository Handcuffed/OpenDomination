import web

from config import *
from cm import render


def toys_gen():
    """Generates checkbox form for toys"""
    return web.form.Form(*[web.form.Checkbox(toy[0], id='t_%s' % toy[0],
           checked=(True if toy[1] == '1' else False)) for toy in
           sorted(items_parser['Toys'].items())] + [web.form.Hidden('form',
           value='toys')])


def clothing_gen():
    """Generates checkbox form for clothing"""
    return web.form.Form(*[web.form.Checkbox(article[0], id='c_%s' %
           article[0], checked=(True if article[1] == '1' else False)) for
           article in sorted(items_parser['Clothing'].items())] +
           [web.form.Hidden('form', value='clothing')])


class Settings:
    def GET(self):
        items_parser.read_string(unicode(open('./static/data/items.CM', 'r').read()))
        return render.settings(toys_gen()(), clothing_gen()())

    def POST(self):
        formdata = web.input()
        if formdata.form == 'toys':
            keys = formdata.keys()
            keys.remove('form')
            for checked in keys:
                items_parser['Toys'][checked] = '1'
            for unchecked in set(items_parser['Toys']) - set(keys):
                items_parser['Toys'][unchecked] = '0'
        elif formdata.form == 'clothing':
            keys = formdata.keys()
            keys.remove('form')
            for checked in keys:
                items_parser['Clothing'][checked] = '1'
            for unchecked in set(items_parser['Clothing']) - set(keys):
                items_parser['Clothing'][unchecked] = '0'

        with open('./static/data/items.CM', 'w') as config:
            items_parser.write(config)
        # New instance of the forms have to be called so they get the updated
        # values from items_parser.
        return render.settings(toys_gen()(), clothing_gen()())
