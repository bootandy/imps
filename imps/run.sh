#! /usr/bin/env python
from imps.imps import Sorter, Style
import sys
import fileinput

data = ''
for line in fileinput.input():
    data += line

print(Sorter(Style.SMARKETS).sort(data))
