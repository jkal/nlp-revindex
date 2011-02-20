#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# tokenize.py
# text tokenizer class
#
# {ikalantzis, vrachnis}@ceid.upatras.gr
#

import re
import HTMLParser

class HTMLTagStripper(HTMLParser.HTMLParser):
    """
    A simple class to strip HTML tags from text, using the HTMLParser module
    from the Python standard library.
    """

    def __init__(self):
        self.reset()
        self.fed = []

    def clear(self):
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)


class Tokenizer(object):
    """ A regular-expression based word tokenizer. """

    def __init__(self):
        self.stripper = HTMLTagStripper()
        self.CONTRACTIONS = [
            re.compile(r"(?i)(.)('ll|'re|'ve|n't|'s|'m|'d)\b")]

    def tokenize(self, text):
        """
        Tokenize text after stripping all html tags.
            text: string to tokenize
        """
        # strip tags
        self.stripper.feed(text)
        text = self.stripper.get_data()
        self.stripper.clear()

        # handle cases like "john's"
        for regexp in self.CONTRACTIONS:
            text = regexp.sub(r'\1 \2', text)

        # separate most punctuation
        text = re.sub(r"([^\w\.\'\-\/,&])", r' \1 ', text)

        # separate commas if they're followed by space (don't separate 2,500)
        text = re.sub(r"(,\s)", r' \1', text)

        # separate single quotes if they're followed by a space.
        text = re.sub(r"('\s)", r' \1', text)

        # separate periods that come before newline or end of string.
        text = re.sub('\. *(\s|\n|$)', ' . ', text)

        return text.split()

# TESTING -- IGNORE
if __name__ == '__main__':
    pass
