from aqt import gui_hooks
from anki import notes
from anki.notes import NoteFieldsCheckResult
import os
from aqt import mw
from aqt.utils import showInfo
from aqt.qt import *
import codecs
import re
from aqt.utils import showInfo, qconnect

def parse_dict():
    def parse_line(d, simpl, line):
        if line[0] == '#':
            return
        parts = line.split('/')[:-1]
        trad = parts[0].split()[0]
        simp = parts[0].split()[1]
        pinyin = parts[0][parts[0].find('[') + 1:parts[0].rfind(']')]
        defs_list = parts[1:]
        d[trad] = {'simplified': simp, 'pinyin': pinyin, 'definitions': defs_list}
        simpl[simp] = {'traditional': trad, 'pinyin': pinyin, 'definitions': defs_list}

    d = {}
    simpl = {}
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, 'cedict_ts.u8')
    with open(filename, encoding='utf-8') as file:
        text = file.read()
        lines = text.split('\n')
        for line in lines:
            parse_line(d, simpl, line)
    return d, simpl

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

chinese_dict, simpl_dict = parse_dict()
symbols = parse_symbols()

def convert_pinyin(pinyin):
    p = pinyin.split()
    return " ".join([symbols[q] if q in symbols else q for q in p])

def check_dupe(note: notes.Note) -> bool:
    status = note.fields_check()
    return status == NoteFieldsCheckResult.DUPLICATE

def check_chinese_sentence(line):
    chrs = sum([ord('A') <= ord(c) <= ord('Z') or ord('a') <= ord(c) <= ord('z') for c in line])
    print("got chrs", chrs, "len", len(line)//2)
    return chrs == 0

def autofill(changed: bool, note: notes.Note, current_field_idx: int) -> bool:
    # changed is always False for some reason in anki
    if note.keys()[current_field_idx].lower() == 'hanzi':
        trad = note.values()[current_field_idx].strip()
        if len(trad) == 0:
            note["Simplified"] = ""
            note["Pinyin"] = ""
            note["Meaning"] = ""
            note["Frequency"] = ""
            return True
        elif not check_dupe(note):
            if trad in chinese_dict:
                simpl = chinese_dict[trad]['simplified']
                pinyin = chinese_dict[trad]['pinyin']
                definitions = chinese_dict[trad]['definitions']
                if simpl:
                    res = lookup_frequency(simpl)
                    if res:
                        permillion, frequency_html = res
                        permillion = str(permillion)
                        # note['permillion'] = permillion
                        note['Frequency'] = frequency_html
                        print(f'found frequency {frequency_html}')
                print(f'found traditional {trad} with simplified {simpl} and pinyin {pinyin} and definitions {definitions}')
                if not note["Simplified"]:
                    note["Simplified"] = simpl
                if not note["Pinyin"]:
                    note["Pinyin"] = convert_pinyin(pinyin)
                if not note["Meaning"]:
                    note["Meaning"] = ', '.join(definitions)
                # return True so the note can be reloaded
                return True
    elif note.keys()[current_field_idx].lower() == 'example sentence':
        print(note["Example sentence"])
        content = note.values()[current_field_idx]
        new_content = ""
        found_replacement = False
        prev = False
        for idx in range(len(content)):
            if not prev and (idx == len(content) - 1 or (idx != len(content) - 1 and not (content[idx] == ' ' and '\u4e00' <= content[idx + 1] <= '\u9fff'))):
                new_content += content[idx]
            if idx != len(content) - 1 and '\u4e00' <= content[idx] <= '\u9fff' and content[idx + 1] == ' ':
                prev = True
                found_replacement = True
            else:
                prev = False
        note['Example sentence'] = new_content
        print("got replacement", note['Example sentence'])
        return found_replacement
    elif note.keys()[current_field_idx].lower() == 'part of speech':
        print(note["Part of speech"])
        pos = note.values()[current_field_idx]
        if pos and pos.endswith("&nbsp;"):
            note['Part of speech'] = pos.replace("&nbsp;", "")
            print("got replace")
            return True
        else:
            return False
    return False

gui_hooks.editor_did_unfocus_field.append(autofill)


# adapted from https://github.com/ernop/anki-chinese-word-frequency
levels = {200: 'very basic',  # 1-477                    = 500                          cum 500
          100: 'basic',  # 477-1016             = 500                          1000
          50: 'very common',  # 1017-2060           = 1000                        2000
          25: 'common',  # 2060-3760          = 1700                        3700
          13: 'uncommon',  # 3760-6313           = 2600                        6300
          7: 'rare',  # 6300-10050         = 3750                        10000
          2: 'very rare',  # 10500-18600        = 8100                        18000
          0: 'obscure'}  # 18600-50000       = 31400                      50000
slevels = sorted(levels.items(), key=lambda x: x[0] * -1)
words = sorted([w.upper() for w in levels.values()], key=lambda x: -1 * len(x))

dirname = os.path.dirname(__file__)
corpus_path = os.path.join(dirname, 'simplified-freqs.num')

if os.path.exists(corpus_path):
    blob = codecs.open(corpus_path, 'r', 'utf8').read()
else:
    showInfo('%s not found.' % corpus_path)


def lookup_frequency(hanzi):
    pat = re.compile('(.+ ' + hanzi + ')\n')
    try:
        res = pat.findall(blob)[0]
    except Exception:
        # ~ showInfo('%s%s'%(repr(e),hanzi))
        # word did not exist in dict.
        return False
    description = ''
    frequency_html = ''
    if res and type(res) != tuple:
        order, permillion, chars = res.split()
        permillion = float(permillion)
        try:
            for num, name in slevels:
                if permillion > num:
                    description = name.upper()
                    frequency_html = name
                    break
        except Exception:
            # ~ showInfo(repr(e))
            return False
    else:
        description = ''
        permillion = ''
        frequency_html = 'unknown'
    return (permillion, frequency_html)


def add_frequency_info():
    cardCount = mw.col.cardCount()
    ii = 0
    # ~ cards=mw.col.findCards('deck:"other"')
    cards = mw.col.findCards('deck:"Chinese"')
    showInfo('got %s cards.  it will take about 1 second for every 10 cards; just let it run.' % str(len(cards)))
    editcount = 0
    for id in cards:
        card = mw.col.getCard(id)
        note = card.note()
        hanzi = None
        changed_this = False
        if 'Frequency' not in note:
            showInfo('you need to add the Frequency field to one of your decks. %s' + repr(note.items()))
            continue
        if note['Hanzi'] in chinese_dict:
            hanzi = chinese_dict[note['Hanzi']]['simplified']
        if hanzi:
            res = lookup_frequency(hanzi)
            if res:
                permillion, frequency_html = res
                permillion = str(permillion)
                editcount += 1
                # note['permillion'] = permillion
                note['Frequency'] = frequency_html
        ii += 1
        note.flush()

    showInfo('changed %d cards.' % editcount)



action = QAction("fill in card info", mw)
qconnect(action.triggered, add_frequency_info)
mw.form.menuTools.addAction(action)