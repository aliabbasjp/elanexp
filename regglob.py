#-------------------------------------------------------------------------------
# Name:        regglob.py
# Purpose:     adapting glob style to allow regex patterns
#
# Author:      Aliabbas Petiwala, IITB
#
# Created:     06/09/2013
# Copyright:   (c)  Aliabbas Petiwala 2013
# Licence:     GNU GPLv3
#-------------------------------------------------------------------------------
#!/usr/bin/env python
import begin,re,os
import glob

def reglob(path, exp, invert=False):
    """glob.glob() style searching which uses regex

    :param exp: Regex expression for filename
    :param invert: Invert match to non matching files
    """

    m = re.compile(exp)

    if invert is False:
        res = [f for f in os.listdir(path) if m.search(f)]
    else:
        res = [f for f in os.listdir(path) if not m.search(f)]

    res = map(lambda x: os.path.join(path,x), res)

    return res

@begin.start
def main():
    print "l"