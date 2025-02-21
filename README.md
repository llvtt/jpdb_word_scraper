# jpdb_word_scraper

## Installation

    python -m pip install -r requirements.txt

## Usage

Find your session cookie by looking in the browser console (e.g. shift-control-i in Firefox), finding a request to JPDB while logged in, and grabbing the cookie from the `Cookie` header. Export it in the shell like this:
```
# Cookie header was 'sid=mycookie'
export JPDB_COOKIE="mycookie"
```
In the same terminal window, you can run the scraper:
```
$ python jpdb_word_scraper/scraper.py --help

usage: scraper.py [-h] [--review-file REVIEW_FILE] [--prev-review-file PREV_REVIEW_FILE] [--output OUTPUT]

optional arguments:
  -h, --help            show this help message and exit
  --review-file REVIEW_FILE, -r REVIEW_FILE
                        JPDB review file JSON
  --prev-review-file PREV_REVIEW_FILE, -p PREV_REVIEW_FILE
                        Previous JPDB review file JSON. Words already present in this file won't be included in the
                        final output.
  --output OUTPUT, -o OUTPUT
                        Output file
```
