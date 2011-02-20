#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# containment.py
# use shingling technique to compute text containment
#
# {ikalantzis,vrachnis}@ceid.upatras.gr
#

import sys
import subprocess
import glob
import operator
import hashlib
import optparse

import lt09.config as config

class Containment(object):

    def __init__(self, inputdir):
        self.files = glob.glob('%s/*.tokens' % inputdir)
        self.shfiles = [ '%s%s' % (x, config.EXT_SHG) for x in self.files ]
        self.docids = [ x.split('_')[-1].split('.')[0] for x in self.files ]

        # Format: { docid:hashlist }
        # hashlist: list with hashes of all shingles
        self.dict = {}

    def hash(self):
        """
        Open file, compute shingles, hash the shingle string and put the
        results in a dictionary.
        """

        print 'Extracting w-shingles, writing files and calculating hashes...',
        sys.stdout.flush()

        for f, shf, docid in zip(self.files, self.shfiles, self.docids):
            hashlist = []
            shingles = self.shingle([line.rstrip() for line in open(f).readlines()])

            # write w-shingles to file
            open(shf, 'w').write('\n'.join([str(x).lower() for x in shingles]))

            # compute hashes, md5 is a bit faster than sha1
            for shingle in shingles:
                hash = hashlib.md5(''.join(shingle)).hexdigest()
                hashlist.append(hash)

            # docid => hashlist
            self.dict[docid] = hashlist
        print 'Done.'

    def shingle(self, txtlist):
        """ Compute and return a list of w-shingles from the given list. """

        shlist = []
        i, j = 0, config.W
        ret = txtlist[0:j]
        while len(ret) > 0:
            shlist.append(ret)
            i += 1
            j += 1
            ret = txtlist[i:j]
        return shlist

    def topfiles(self):
        """
        Find and return the 5 largest files in the collection.
        More shingles = more words, more words = larger file.
        """

        length = {}
        for docid in self.dict.keys():
            length[docid] = len(self.dict[docid])

        # sort the list and get the top 5 elements
        docs = sorted(length.items(), key=operator.itemgetter(1), reverse=1)

        print 'Top files:', docs[:5]

        return [d[0] for d in docs[:5]]

    def calculate(self, verbose):
        """
        Main routine. Calculate the intersections of shinglings lists and
        calculate the containment.
            http://en.wikipedia.org/wiki/W-shingling
        """

        self.hash()

        for topdocid in self.topfiles():
            containment = 0
            for docid, hashlist in self.dict.iteritems():
                if docid != topdocid:
                    intersection = set(self.dict[topdocid]).intersection(hashlist)
                    if verbose:
                        print '%s in %s: %s' % (topdocid, docid, len(intersection))
                    containment += len(intersection)

            totalsize = 0
            for key in self.dict.keys():
                totalsize += len(self.dict[key])
            totalsize -= len(self.dict[topdocid])

            percent = float(containment) / float(totalsize) * 100
            print 'Total containment of %s is %s percent' % (topdocid, percent)

if __name__ == '__main__':
    usage = "usage: %prog [options]"

    parser = optparse.OptionParser(usage=usage)
    parser.add_option('-d', '--dir', dest='inputdir', default=config.FILEDIR, help='Specify a different input directory.')
    parser.add_option('--nojit', action='store_true', dest='nojit', default=False, help='Do not use Psyco Just-In-Time compiler.')
    parser.add_option('-v', '--verbose', action='store_true', dest='verbose', default=False, help='Display intersections of all file pairs.')

    (options, args) = parser.parse_args()

    if not options.nojit:
        try:
            import psyco
            psyco.full()
            print "Psyco is available. Fasten your seatbelts."
        except ImportError:
            print "Psyco not available."

    Containment(options.inputdir).calculate(options.verbose)
