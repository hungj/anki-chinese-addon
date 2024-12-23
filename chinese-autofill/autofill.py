from anki import notes
from anki.notes import NoteFieldsCheckResult
from .chinese_dictionary import ChineseDictionary
from .utils import *


def _check_dupe(note: notes.Note) -> bool:
    status = note.fields_check()
    return status == NoteFieldsCheckResult.DUPLICATE

_chinese_dict = ChineseDictionary()
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
        elif not _check_dupe(note):
            entry = _chinese_dict.get_entry(trad)
            if entry:
                if entry.simplified:
                    res = lookup_frequency(entry.simplified)
                    if res:
                        permillion, frequency_html = res
                        permillion = str(permillion)
                        # note['permillion'] = permillion
                        note['Frequency'] = frequency_html
                        print(f'found frequency {frequency_html}')
                print(f'found traditional {trad} with simplified {entry.simplified} and pinyin {entry.pinyin} and definitions {entry.definitions}')
                if not note["Simplified"]:
                    note["Simplified"] = entry.simplified
                if not note["Pinyin"]:
                    note["Pinyin"] = convert_pinyin(entry.pinyin)
                if not note["Meaning"]:
                    note["Meaning"] = ', '.join(entry.definitions)
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