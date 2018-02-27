"""
Usage:
  python wrangle.py scan_title_basics
Options:
  -h --help     Show this screen.
  --version     Show version.
"""

# Chris Joakim, Microsoft, 2018/02/27

import csv
import json
import sys
import time
import os

from docopt import docopt

from pysrc.joakim import config


VERSION='2018/02/27a'


class Main:

    def __init__(self):
        self.start_time = time.time()
        self.args = sys.argv
        self.c = config.Config()
        #print('data_dir: {}'.format(self.c.data_dir()))

    def execute(self):
        if len(sys.argv) > 1:
            f = sys.argv[1].lower()
            print('function: {}'.format(f))

            if f == 'extract_top_ratings':
                self.extract_top_ratings()

            elif f == 'extract_top_movies':
                self.extract_top_movies()

            elif f == 'scan2':
                pass
            else:
                self.print_options('Error: invalid function: {}'.format(f))
        else:
            self.print_options('Error: no function argument provided.')

    def extract_top_ratings(self):
        # Identify and extract the top (movie) ratings with at least 10000 votes
        infile = self.c.data_filename('title.ratings.tsv')
        outfile = self.c.top_ratings_csv_filename()
        row_count = 0
        min_votes = 10000
        selected  = dict()

        with open(infile) as tsvfile:
            reader = csv.DictReader(tsvfile, dialect='excel-tab')
            for row in reader:
                # OrderedDict([('tconst', 'tt0000001'), ('averageRating', '5.8'), ('numVotes', '1349')])
                try:
                    row_count = row_count + 1
                    votes = int(row['numVotes'])
                    if votes > min_votes:
                        id = row['tconst']
                        selected[id] = votes
                    # if row_count < 10:
                    #     print(row)
                    #     print(row['tconst'])
                except:
                    print('exception on row {} {}'.format(row_count, row))

        print("extract_top_ratings - selected count: {}".format(len(selected.keys())))

        with open(outfile, "w", newline="\n") as out:
            out.write("id|votes\n")
            for id in sorted(selected.keys()):
                votes = selected[id]
                line  = '{}|{}'.format(id.strip(), votes)
                out.write(line + "\n")
            print('file written: {}'.format(outfile))

        elapsed_time = time.time() - self.start_time
        print('lines_read: {}  elapsed: {}'.format(row_count, elapsed_time))
        # lines_read: 4832632  elapsed: 25.33212375640869

    def extract_top_movies(self):
        infile = self.c.data_filename('title.basics.tsv')
        outfile = self.c.top_movies_csv_filename()
        selected = dict()
        row_count = 0
        top_rated = self.load_top_ratings()

        with open(infile) as tsvfile:
            reader = csv.DictReader(tsvfile, dialect='excel-tab')
            for row in reader:
                # OrderedDict([('tconst', 'tt0000009'), ('titleType', 'movie'), ('primaryTitle', 'Miss Jerry'),
                # ('originalTitle', 'Miss Jerry'), ('isAdult', '0'), ('startYear', '1894'), ('endYear', '\\N'),
                # ('runtimeMinutes', '45'), ('genres', 'Romance')])
                try:
                    row_count = row_count + 1
                    id = row['tconst']
                    if id in top_rated:
                        if 'movie' == row['titleType']:
                            if '0' == row['isAdult']:
                                title = row['primaryTitle']
                                selected[id] = title
                                #print('selected top_rated item {} {}'.format(id, title))
                except:
                    print('exception on row {} {}'.format(row_count, row))

        print("extract_top_movies - selected count: {}".format(len(selected.keys())))

        with open(outfile, "w", newline="\n") as out:
            out.write("id|title\n")
            for id in sorted(selected.keys()):
                title = selected[id]
                line  = '{}|{}'.format(id.strip(), title.strip())
                out.write(line + "\n")
            print('file written: {}'.format(outfile))

    # private

    def load_top_ratings(self):
        infile1 = self.c.top_ratings_csv_filename()
        top_rated = dict()
        row_count = 0
        with open(infile1) as csvfile:
            reader = csv.reader(csvfile, delimiter='|')
            for row in reader:
                # ['tt0000417', '34795']
                try:
                    row_count = row_count + 1
                    if row_count > 1:
                        id = row[0]
                        top_rated[id] = 0
                except:
                    print('exception on row {} {}'.format(row_count, row))
        print('loaded the top_rated ids; count: {}'.format(len(top_rated.keys())))
        return top_rated

    def print_options(self, msg):
        print(msg)
        arguments = docopt(__doc__, version=VERSION)
        print(arguments)


Main().execute()