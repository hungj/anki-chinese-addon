from aqt import mw
from .chinese_dictionary import ChineseDictionary
from .utils import *


_chinese_dict = ChineseDictionary()
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
                editcount += 1
                # note['permillion'] = permillion
                note['Frequency'] = frequency_html
        ii += 1
        note.flush()

    showInfo('changed %d cards.' % editcount)