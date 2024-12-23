import codecs
import re

from aqt.qt import *
from aqt.utils import showInfo
from .constants import *


def get_resource_path(filename):
    dirname = os.path.dirname(__file__)
    return os.path.join(dirname, "resources", filename)

def _parse_symbols():
    symbols = {}
    path = get_resource_path('ch_symbols.csv')
    with open(path, encoding='utf-8') as file:
        text = file.read()
        lines = text.split('\n')
        for line in lines:
            if line:
                parts = line.split(',')
                symbols[parts[0]] = parts[1]
    return symbols

symbols = _parse_symbols()

def convert_pinyin(pinyin):
    """Convert pinyin numbers to accents.

    :param pinyin: space separated pinyin to convert, e.g. dian4 nao3
    :return: pinyin with accent marks
    """
    p = pinyin.split()
    return " ".join([symbols[q] if q in symbols else q for q in p])

def check_chinese_sentence(line):
    """Check if a sentence is Chinese; current logic is if it doesn't contain any English characters.

    :param line: string to check
    :return: True if it is Chinese
    """
    chrs = sum([ord('A') <= ord(c) <= ord('Z') or ord('a') <= ord(c) <= ord('z') for c in line])
    return chrs == 0

# adapted from https://github.com/ernop/anki-chinese-word-frequency
LEVELS = {200: Frequency.VERY_BASIC.value,  # 1-477                    = 500                          cum 500
          100: Frequency.BASIC.value,  # 477-1016             = 500                          1000
          50: Frequency.VERY_COMMON.value,  # 1017-2060           = 1000                        2000
          25: Frequency.COMMON.value,  # 2060-3760          = 1700                        3700
          13: Frequency.UNCOMMON.value,  # 3760-6313           = 2600                        6300
          7: Frequency.RARE.value,  # 6300-10050         = 3750                        10000
          2: Frequency.VERY_RARE.value,  # 10500-18600        = 8100                        18000
          0: Frequency.OBSCURE.value}  # 18600-50000       = 31400                      50000
COLORS = {Frequency.VERY_BASIC.value: "#07f50b",
          Frequency.BASIC.value: "#02f55b",
          Frequency.VERY_COMMON.value: "#00f090",
          Frequency.COMMON.value: "#02f0b0",
          Frequency.UNCOMMON.value: "#02a2f7",
          Frequency.RARE.value: "#bb30f0",
          Frequency.VERY_RARE.value: "#f0072a",
          Frequency.OBSCURE.value: "#a8a7a7"}
slevels = sorted(LEVELS.items(), key=lambda x: x[0] * -1)
words = sorted([w.upper() for w in LEVELS.values()], key=lambda x: -1 * len(x))

corpus_path = get_resource_path('simplified-freqs.num')

if os.path.exists(corpus_path):
    blob = codecs.open(corpus_path, 'r', 'utf8').read()
else:
    showInfo('%s not found.' % corpus_path)


def lookup_frequency(hanzi_simplified):
    """Look up frequency of a simplified hanzi word.

    :param hanzi_simplified: Simplified hanzi to look up frequency for
    :return: tuple of (permillion, frequency)
    """
    pat = re.compile('(.+ ' + hanzi_simplified + ')\n')
    try:
        res = pat.findall(blob)[0]
    except Exception:
        # word did not exist in dict.
        return False
    frequency_html = ''
    if res and type(res) != tuple:
        _, permillion, chars = res.split()
        permillion = float(permillion)
        try:
            for num, name in slevels:
                if permillion > num:
                    description = name.upper()
                    frequency_html = '<span style="color:%s">%s</span>' % (COLORS[name], name)
                    break
        except Exception:
            return False
    else:
        permillion = ''
        frequency_html = 'unknown'
    return (permillion, frequency_html)