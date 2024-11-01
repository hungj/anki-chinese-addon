from aqt import gui_hooks
from anki import notes
from anki.notes import NoteFieldsCheckResult
import os


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

chinese_dict = parse_dict()
symbols = parse_symbols()

def convert_pinyin(pinyin):
    p = pinyin.split()
    return " ".join([symbols[q] if q in symbols else q for q in p])

def check_dupe(note: notes.Note) -> bool:
    status = note.fields_check()
    return status == NoteFieldsCheckResult.DUPLICATE

def autofill(changed: bool, note: notes.Note, current_field_idx: int) -> bool:
    # changed is always False for some reason in anki
    if note.keys()[current_field_idx].lower() == 'hanzi':
        print(note["Example sentence"])
        trad = note.values()[current_field_idx].strip()
        if len(trad) == 0:
            note["Simplified"] = ""
            note["Pinyin"] = ""
            note["Meaning"] = ""
            return True
        elif not check_dupe(note):
            if trad in chinese_dict:
                simpl = chinese_dict[trad]['simplified']
                pinyin = chinese_dict[trad]['pinyin']
                definitions = chinese_dict[trad]['definitions']
                print(f'found traditional {trad} with simplified {simpl} and pinyin {pinyin} and definitions {definitions}')
                if not note["Simplified"]:
                    note["Simplified"] = simpl
                if not note["Pinyin"]:
                    note["Pinyin"] = convert_pinyin(pinyin)
                if not note["Meaning"]:
                    note["Meaning"] = ', '.join(definitions)
                # return True so the note can be reloaded
                return True
    return False

gui_hooks.editor_did_unfocus_field.append(autofill)