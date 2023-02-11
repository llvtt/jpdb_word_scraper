#!/usr/bin/env python

import dataclasses
import typing

import bs4
import requests
# noinspection PyUnresolvedReferences
import lxml


@dataclasses.dataclass
class Word:
    spelling: str
    reading: str
    definitions: list[str]
    parts_of_speech: list[str]
    notes: str | None
    sentence: str


cookie = "sid=cf0dc7888fb90a1eb190f8873e0e7fb2"

headers = {
    "authority": "jpdb.io",
    "sec-ch-ua": "^^",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "^^",
    "upgrade-insecure-requests": "1",
    "dnt": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "ja,en-GB;q=0.9,en;q=0.8",
    "cookie": cookie,
    "if-none-match": "^^",
}

word_url = "https://jpdb.io/vocabulary/1429200/%E8%AA%BF%E6%95%B4/%E3%81%A1%E3%82%87%E3%81%86%E3%81%9B%E3%81%84?lang=english#a"


class ParseError(Exception):
    pass


def _japanese_strings(tag_with_text):
    """Yield substrings of the japanese text markup without furigana."""
    for child in tag_with_text.children:
        if isinstance(child, str):
            yield child
        elif child.name == 'rt':
            # Furigana
            pass
        else:
            yield from _japanese_strings(child)


def _strip_furigana(tag):
    """Return text content of the tag without furigana."""
    return ''.join(_japanese_strings(tag))


def get_word_info() -> Word:
    response = requests.get(word_url, headers=headers)
    response.encoding = 'UTF-8'
    soup = bs4.BeautifulSoup(response.text, 'lxml')

    # spelling
    spelling_section = soup.find('div', class_='spelling')
    if not spelling_section:
        raise ParseError("could not find spelling")
    spelling = _strip_furigana(spelling_section)

    accent_section = soup.find('div', class_='subsection-pitch-accent')
    if not isinstance(accent_section, bs4.element.Tag):
        raise ParseError("could not find subsection-pitch-accent")
    accent_content = accent_section.find('div', class_='subsection')
    if not isinstance(accent_content, bs4.element.Tag):
        raise ParseError("could not find subsection-pitch-accent content")
    reading = accent_content.text

    # meanings
    meanings = soup.find('div', class_='subsection-meanings')
    if not isinstance(meanings, bs4.element.Tag):
        raise ParseError("could not find subsection-meanings")

    definitions = [meaning.text for meaning in meanings.find_all('div', class_='description')]

    # part of speech
    pos_section = meanings.find('div', class_='part-of-speech')
    if not isinstance(pos_section, bs4.element.Tag):
        raise ParseError("could not find part-of-speech section")
    pos_list = [pos.text for pos in pos_section.children]

    # custon definition (may not be present?)
    custom_meaning = meanings.find('div', class_='custom-meaning')
    if custom_meaning:
        notes = custom_meaning.text.strip()
    else:
        notes = None

    # custom sentence (may not be present?)
    sentence = _strip_furigana(soup.find('div', class_='card-sentence'))

    return Word(
        spelling=spelling,
        reading=reading,
        definitions=definitions,
        parts_of_speech=pos_list,
        notes=notes,
        sentence=sentence,
    )


def main():
    word = get_word_info()
    print(word)


if __name__ == '__main__':
    main()
