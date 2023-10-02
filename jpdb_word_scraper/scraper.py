#!/usr/bin/env python

import csv
import dataclasses
import itertools
import json
import os
import re
import time
import typing

import bs4
# noinspection PyUnresolvedReferences
import lxml
import requests


@dataclasses.dataclass
class Word:
    spelling: str
    reading: typing.Optional[str]
    definitions: str
    parts_of_speech: str
    notes: typing.Optional[str]
    sentence: typing.Optional[str]


class ParseError(Exception):
    pass


def strings_to_html_list(strings: typing.List[str]) -> str:
    pattern = re.compile(r"^\d\. ")
    elements = [
        f"<li>{re.sub(pattern, '', element)}</li>"
        for element in strings
    ]
    return f"<ol>{elements}</ol>"


class JPDBScraper:
    def __init__(self, cookie):
        self._session_cookie = cookie
        self._http_client = None

    def _japanese_strings(self, tag_with_text):
        """Yield substrings of the japanese text markup without furigana."""
        for child in tag_with_text.children:
            if isinstance(child, str):
                yield child
            elif child.name == 'rt':
                # Furigana
                pass
            else:
                yield from self._japanese_strings(child)

    def _strip_furigana(self, tag):
        """Return text content of the tag without furigana."""
        return ''.join(self._japanese_strings(tag))

    def _headers(self) -> dict:
        return {
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
            "cookie": self._session_cookie,
            "if-none-match": "^^",
        }

    def lookup_word(self, spelling) -> Word:
        url = f"https://jpdb.io/search?q={spelling}&lang=english#a"
        response = requests.get(url, headers=self._headers())
        response.encoding = 'UTF-8'
        soup = bs4.BeautifulSoup(response.text, 'lxml')

        # reading
        accent_section = soup.find('div', class_='subsection-pitch-accent')
        reading = None
        if isinstance(accent_section, bs4.element.Tag):
            accent_content = accent_section.find('div', class_='subsection')
            if isinstance(accent_content, bs4.element.Tag):
                reading = accent_content.text

        # meanings
        meanings = soup.find('div', class_='subsection-meanings')
        if not isinstance(meanings, bs4.element.Tag):
            raise ParseError("could not find subsection-meanings")

        definitions = [
            " ".join(meaning.strings)
            for meaning in meanings.find_all('div', class_='description')
        ]

        # part of speech
        pos_section = meanings.find('div', class_='part-of-speech')
        if not isinstance(pos_section, bs4.element.Tag):
            raise ParseError("could not find part-of-speech section")
        pos_list = [pos.text for pos in pos_section.children]

        # custon definition (may not be present)
        custom_meaning = meanings.find('div', class_='custom-meaning')
        if custom_meaning:
            notes = "".join(str(element) for element in custom_meaning.contents)
        else:
            notes = None

        # custom sentence (may not be present)
        sentence_section = soup.find('div', class_='card-sentence')
        if sentence_section:
            sentence = self._strip_furigana(sentence_section)
        else:
            sentence = None

        return Word(
            spelling=spelling,
            reading=reading,
            definitions=strings_to_html_list(definitions),
            parts_of_speech=", ".join(pos_list),
            notes=notes,
            sentence=sentence,
        )


cookie = os.getenv("JPDB_COOKIE")


def collect_words(words: typing.List[str]):
    scraper = JPDBScraper(cookie)
    lookup = []
    for i, word in enumerate(words, 1):
        print(f"({i}/{len(words)}) looking up word {word}")
        lookup.append(scraper.lookup_word(word))
        time.sleep(1)

    return lookup


def build_csv(words: typing.List[Word]) -> None:
    with open("jpdb_words.csv", "w") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=[field.name for field in dataclasses.fields(Word)])
        writer.writeheader()

        for word in words:
            writer.writerow(dataclasses.asdict(word))


def review_words(jpdb_reviews: dict) -> typing.List[str]:
    return list({
        entry["spelling"] for entry in itertools.chain(
            jpdb_reviews["cards_vocabulary_jp_en"],
            jpdb_reviews["cards_vocabulary_en_jp"],
        )
    })


def main():
    review_file = "reviews.json"
    with open(review_file) as reviewfile:
        reviews = json.load(reviewfile)

    words = review_words(reviews)
    lookup = collect_words(words)
    build_csv(lookup)


if __name__ == '__main__':
    main()

# def old_main():
#     scraper = JPDBScraper(cookie)
#     word = scraper.lookup_word("故郷")
#     print(word)
