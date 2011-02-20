#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# config.py
# configuration and environment variables
#
# {ikalantzis,vrachnis}@ceid.upatras.gr
#

# Tagger related paths
TAGGERBIN = './tools/tree-tagger-osx'
TAGGERDICT = './tools/english-par-linux-3.1.bin'

# Default data paths
FILEDIR = './wikipedia'
XMLOUTPUT = 'output.xml'

# File extensions
EXT_TOK = '.tokens'
EXT_TAG = '.tags'
EXT_DICT = '.dict'
EXT_SHG = '.shingles'

# Shingle size
W = 4

UNKNOWNTAG = '<unknown>'
