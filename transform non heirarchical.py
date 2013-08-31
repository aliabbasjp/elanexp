#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      ALI
#
# Created:     31/08/2013
# Copyright:   (c) ALI 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python
import json

eafj='E:\elan projects\L2\L2v1f_DIP.eaf.379.json'

def main():
    j= json.load(open(eafj))
    for (k,v) in  j.iteritems():
        for (a,b) in v.iteritems():
            if a!='transcript':
                v[a]=b[1]

    json.dump(j,open(eafj,'w'),indent=4)




if __name__ == '__main__':
    main()
