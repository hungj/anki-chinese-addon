# import the main window object (mw) from aqt
from aqt import gui_hooks, mw
# import the "show info" tool from utils.py
from aqt.utils import showInfo, qconnect
# import all of the Qt GUI library
from aqt.qt import *
from anki import notes
import requests
import os


# We're going to add a menu item below. First we want to create a function to
# be called when the menu item is activated.

def parse_dict():
    def parse_line(d, line):
        if line[0] == '#':
            return
        parts = line.split('/')[:-1]
        trad = parts[0].split()[0]
        simp = parts[0].split()[1]
        pinyin = parts[0][parts[0].find('[') + 1:parts[0].rfind(']')]
        defs_list = parts[1:]
        d[trad] = {'simplified': simp, 'pinyin': pinyin, 'definitions': defs_list}

    d = {}
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, 'cedict_ts.u8')
    with open(filename, encoding='utf-8') as file:
        text = file.read()
        lines = text.split('\n')
        for line in lines:
            parse_line(d, line)
    return d

d = parse_dict()

def parse_symbols():
    symbols = {}
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, 'ch_symbols.csv')
    with open(filename, encoding='utf-8') as file:
        text = file.read()
        lines = text.split('\n')
        for line in lines:
            if line:
                parts = line.split(',')
                symbols[parts[0]] = parts[1]
    return symbols
symbols = parse_symbols()

def convert_pinyin(pinyin):
    p = pinyin.split()
    return " ".join([symbols[q] if q in symbols else q for q in p])

def testFunction(changed: bool, note: notes.Note, current_field_idx: int) -> bool:
    # get the number of cards in the current collection, which is stored in
    # the main window
    # cardCount = mw.col.cardCount()
    # show a message box
    # print(f"changed: {changed}, current_field_idx: {current_field_idx}")
    #if changed and note.keys()[current_field_idx].lower() == 'hanzi':
    # changed is always False for some reason in anki
    if note.keys()[current_field_idx].lower() == 'hanzi':
        trad = note.values()[current_field_idx].strip()
        if trad in d:
            simpl = d[trad]['simplified']
            pinyin = d[trad]['pinyin']
            definitions = d[trad]['definitions']
            print(f'found traditional {trad} with simplified {simpl} and pinyin {pinyin} and definitions {definitions}')
            if not note["Simplified"]:
                note["Simplified"] = simpl
            if not note["Pinyin"]:
                note["Pinyin"] = convert_pinyin(pinyin)
            if not note["Meaning"]:
                note["Meaning"] = ', '.join(definitions)
            # return true so the note can be reloaded
            return True
    return False

    # for key, value in note.items():
    #    print(f"for note {note.id}, got key {key} and value {value}")

gui_hooks.editor_did_unfocus_field.append(testFunction)

# create a new menu item, "test"
#action = QAction("test", mw)
# set it to call testFunction when it's clicked
#qconnect(action.triggered, testFunction)
# and add it to the tools menu
#mw.form.menuTools.addAction(action)