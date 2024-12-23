from dataclasses import dataclass
from .utils import get_resource_path


@dataclass
class ChineseWord:
    traditional: str
    simplified: str
    pinyin: str
    definitions: list[str]

class ChineseDictionary:
    def __init__(self):
        self.chinese_dict = self._parse()

    def _parse(self):
        def parse_line(d, line):
            if line[0] == '#':
                return
            parts = line.split('/')[:-1]
            trad = parts[0].split()[0]
            simp = parts[0].split()[1]
            pinyin = parts[0][parts[0].find('[') + 1:parts[0].rfind(']')]
            defs_list = parts[1:]
            d[trad] = ChineseWord(traditional=trad, simplified=simp, pinyin=pinyin, definitions=defs_list)

        d = {}
        filename = get_resource_path('cedict_ts.u8')
        with open(filename, encoding='utf-8') as file:
            text = file.read()
            lines = text.split('\n')
            for line in lines:
                parse_line(d, line)
        return d

    def get_entry(self, traditional):
        """Get entry in dictionary from traditional hanzi, None if it doesn't exist

        :param traditional: traditional hanzi
        :return: ChineseWord entry
        """
        if traditional not in self.chinese_dict:
            return None
        return self.chinese_dict[traditional]