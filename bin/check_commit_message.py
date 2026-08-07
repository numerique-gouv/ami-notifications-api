#! /usr/bin/python3

import re
import sys

with open(sys.argv[1]) as fd:
    subject_line = fd.readline()
    if not re.match(r".*\(#\d+\)$", subject_line):
        print("Your subject first line should end with an issue number")
        sys.exit(1)
