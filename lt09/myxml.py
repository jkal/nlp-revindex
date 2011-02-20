#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# xml.py
# XML handling module
#
# {ikalantzis, vrachnis}@ceid.upatras.gr
#

import sys

try:
    from lxml import etree
    lxml_loaded = True
except ImportError, e:
    print e
    lxml_loaded = False
    try:
        import xml.etree.cElementTree as etree
        print 'Running with xml.etree.cElementTree.'
    except ImportError, e:
        print e
        try:
            import cElementTree as etree
            print 'Running with standard cElementTree.'
        except ImportError, e:
            print e
            print "No suitable XML library found. Aborting. Install python-lxml."
            sys.exit(1)

class XMLHandler(object):

    def xcreate(self, dictionary, outfile):
        lemmas = dictionary.keys()
        rootnode = etree.Element('inverted_index')
        for lemma in lemmas:
            lemmanode = etree.SubElement(rootnode, 'lemma', attrib={'name' : lemma})

            docs = dictionary[lemma].keys()
            for eachdoc in docs:
                docnode = etree.SubElement(lemmanode, 'document', attrib={'id' : eachdoc, 'weight' : dictionary[lemma][eachdoc]})

        if lxml_loaded:
            etree.ElementTree(rootnode).write(outfile, xml_declaration=True, pretty_print=True, encoding='utf-8')
        else:
            try:
                etree.ElementTree(rootnode).write(open(outfile, 'w'))
            except TypeError, e:
                print e, 'Just use lxml.'

    def xload(self, infile):
        try:
            self.doc = etree.parse(infile)
        except IOError, e:
            print "Execution failed:", e
            sys.exit(1)

    def xsearch(self, search_term):
        dict = {}
        for x in self.doc.findall('/lemma[@name="%s"]/*' % search_term):
            dict[x.attrib['id']] = x.attrib['weight']
        return dict

# TESTING -- IGNORE
if __name__ == '__main__':
    pass
