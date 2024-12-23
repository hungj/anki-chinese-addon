from aqt import mw
from .chinese_dictionary import ChineseDictionary
from .utils import *


_LOG_FREQ = 100
_chinese_dict = ChineseDictionary()
def add_frequency_info():
    ii = 0
    cards = mw.col.find_cards('deck:"Chinese"')
    card_count = len(cards)
    edit_count = 0
    for id in cards:
        card = mw.col.get_card(id)
        note = card.note()
        if 'Frequency' not in note:
            showInfo('you need to add the Frequency field to one of your decks. %s' + repr(note.items()))
            continue
        simplified_hanzi = None
        entry = _chinese_dict.get_entry(note['Hanzi'])
        if entry:
            simplified_hanzi = entry.simplified
        if simplified_hanzi:
            res = lookup_frequency(simplified_hanzi)
            if res:
                permillion, frequency_html = res
                permillion = str(permillion)
                edit_count += 1
                # note['permillion'] = permillion
                note['Frequency'] = frequency_html
        ii += 1
        if ii % _LOG_FREQ == 0:
            print(f"Processed {ii} / {card_count} cards ({'%.1f' % (float(ii) / card_count*100)}%)")
        mw.col.update_note(note)
    print(f"Processed {ii} / {card_count} cards ({'%.1f' % (float(ii) / card_count * 100)}%)")

    showInfo('Changed %d cards.' % edit_count)