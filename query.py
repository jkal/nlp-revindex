#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# query.py
# make queries to the index
#
# {ikalantzis,vrachnis}@ceid.upatras.gr
#

import sys
import os
import optparse
import time
import operator

import lt09.myxml as myxml
import lt09.config as config

def lookup(xml, query, verbose):
    """ Search for the specified term. May be a single word or a text file. """

    start = time.time()

    if ' ' in query:
        terms = query.split()

        docs = []
        for term in terms:
            docs.append(xml.xsearch(term))

        documents = docs[0].keys()
        for doc in docs[1:]:
            documents = list(set(documents) & set(doc.keys()))

        result = {}
        for docid in documents:
             for doc in docs:
                 result[docid] = result.get(docid, 0) + float(doc[docid])
    else:
        result = xml.xsearch(query)

    end = time.time()

    res = sorted(result.items(), key=operator.itemgetter(1), reverse=1)

    print '\nResults for %s: %s' % (query, len(res))
    if options.verbose:
        for answer in res: print answer[0], ':', answer[1]
    print 'Query took: %s seconds ' % (end - start)

if __name__ == '__main__':
    usage = 'usage: %prog [options] <XML file> <search term or file>'

    parser = optparse.OptionParser(usage=usage)
    parser.add_option('--nojit', action='store_true', dest='nojit', default=False, help='Do not use Psyco Just-In-Time compiler.')
    parser.add_option('-v', '--verbose', action='store_true', dest='verbose', default=False, help='Spam the screen with info.')

    (options, args) = parser.parse_args()

    if len(args) < 2:
        parser.error('incorrect number of arguments')
    else:
        xmlfile = args[0]
        query = args[1]

    if not options.nojit:
        try:
            import psyco
            psyco.full()
            print "Psyco is available. Fasten your seatbelts."
        except ImportError:
            print "Psyco not available."

    x = myxml.XMLHandler()
    x.xload(xmlfile)

    try:
        for q in open(query):
            lookup(x, q.rstrip(), options.verbose)
    except:
        lookup(x, query, options.verbose)
