#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# build_index.py
# parse all input files to create the inverted index and all the intermediate files
#
# {ikalantzis,vrachnis}@ceid.upatras.gr
#

import sys
import glob
import codecs
import tempfile
import subprocess
import math
import optparse

import lt09.tokenize as tok
import lt09.config as config
import lt09.myxml as myxml

class Runner(object):

    def __init__(self, inputdir):
        self.files = glob.glob('%s/*.txt' % inputdir)
        self.tokfiles = [ '%s%s' % (x, config.EXT_TOK) for x in self.files ]
        self.tagfiles = [ '%s%s' % (x, config.EXT_TAG) for x in self.files ]
        self.dictfiles = [ '%s%s' % (x, config.EXT_DICT) for x in self.files ]
        self.docids = [ x.split('_')[-1].split('.')[0] for x in self.files ]
        self.inverted_dict = {}
        self.dictionary = {}
        self.wc = {}
        self.n = len(self.files)
        self.words = 0

    def tokenize(self):
        """ Invoke the tokenizer to split the files into tokens. """

        t = tok.Tokenizer()
        for i, (file, tokfile) in enumerate(zip(self.files, self.tokfiles), start=1):
            print '(%s/%s) Tokenizing: %s\r' % (i, self.n, file),

            fin = codecs.open(file, 'r', 'utf-8')
            fout = codecs.open(tokfile, 'w', 'utf-8')

            fout.write('\n'.join(t.tokenize(fin.read())))

            fout.close()
            fin.close()

    def tag(self):
        """
        Spawn a new process of an external PoS tagger (in this case TreeTagger).
        Usage of another tagger may require minor changes.
        """

        # create a temp file with input/output files to pass to the tagger
        f = tempfile.NamedTemporaryFile()
        for tokfile, tagfile in zip(self.tokfiles, self.tagfiles):
            f.write('%s %s\n' % (tokfile, tagfile))
        f.flush()
        print '\nTagging...',
        sys.stdout.flush()

        try:
            subprocess.call([config.TAGGERBIN, config.TAGGERDICT, '-quiet', '-token', '-lemma', '-files', f.name])
        except OSError, e:
            print "\nExecution failed:", e
            sys.exit(1)

        print 'Done.'

    def create_index(self):

        self.tokenize()
        self.tag()

        # tag values to remove
        rmvalues = ('CD', 'CC', 'DT', 'EX', 'IN', 'LS', 'MD', 'PDT', 'POS',
                    'PRP', 'PRP$', 'RP', 'TO', 'UH', 'WDT', 'WP', 'WP$',
                    'WRB', 'SENT', ':', ',', "''", '(', ')', '$', '"', '%')

        print 'Creating dictionaries...',
        sys.stdout.flush()

        for tagfile, dictfile, docid in zip(self.tagfiles, self.dictfiles, self.docids):
            fin = open(tagfile, 'r')
            dic = {}
            for line in fin:
                tag, lemma = line.rstrip().lower().split('\t')[1:]

                if tag.upper() not in rmvalues:
                    self.words += 1
                    self.wc[docid] = self.wc.get(docid, 0) + 1
                    dic[lemma] =  [ dic.get(lemma, [0, tag])[0] + 1, tag ]

            try:
                # rm 'unknown' lemmas
                del dic[config.UNKNOWNTAG]
            except KeyError:
                print '\nNo unknown lemmas found.'

            # write dictionary file
            fout = open(dictfile, 'w')
            for (lemma, count) in dic.iteritems():
                fout.write("%s %s %s\n" % (lemma, count[1].upper(), count[0]))
            fout.close()

            # push dictionary in a dictionary with <docid:dictionary>
            for key, val in dic.iteritems():
                temp = self.inverted_dict.get(key, {})
                temp[docid] = val[0]
                self.inverted_dict[key] = temp

        print 'Done.'

        r.weight()

    def weight(self):
        """ Compute weights on the inverted index. """

        print 'Computing weights...',
        sys.stdout.flush()
        for key, val in self.inverted_dict.iteritems():
            for docid, count in val.iteritems():
                tf = float(count) / self.wc[docid]
                idf = math.log10(float(self.n) / len(val))
                w = tf * idf
                val[docid] = '%.8f' % w
            self.dictionary[key] = val
        print 'Done.'

    def genxml(self, xmlfile):
        """ Use the lt09.xml module to generate the XML output. """

        print 'Generating XML...',
        sys.stdout.flush()
        x = myxml.XMLHandler()
        x.xcreate(self.dictionary, xmlfile)
        print 'Done.'

    def statistics(self):
        print 'Total lemmas in collection: %s' % self.words
        print 'Total unique lemmas in collection: %s' % len(self.dictionary)

if __name__ == '__main__':
    usage = "usage: %prog [options]"

    parser = optparse.OptionParser(usage=usage)
    parser.add_option('-d', '--dir', dest='inputdir', default=config.FILEDIR, help='Specify a different input directory.')
    parser.add_option('-o', '--output', dest='output', default=config.XMLOUTPUT, help='Give an alternative XML filename.')
    parser.add_option('--nojit', action='store_true', dest='nojit', default=False, help='Do not use Psyco Just-In-Time compiler.')

    (options, args) = parser.parse_args()

    if not options.nojit:
        try:
            import psyco
            psyco.full()
            print "Psyco is available. Fasten your seatbelts."
        except ImportError:
            print "Psyco not available."

    r = Runner(options.inputdir)

    try:
        r.create_index()
        r.genxml(options.output)
        print 'All done.'
        r.statistics()
    except:
        print 'Unexpected error:', sys.exc_info()[0]
        raise
