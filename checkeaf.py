#-------------------------------------------------------------------------------
# Name:     checkeaf
# Purpose:  check elan eaf xml files
#
# Author:      ALI
#
# Created:     31/08/2013
# Copyright:   (c) ALI 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python
import warnings
warnings.filterwarnings("ignore")
from elan2json import elan2json
from json2taskdata import readjson
from globalerror import Errors
import begin


#@begin.start
def checkeaf(eafpath=r'E:\elan projects\L2\submissions\extracted\L2_100020050.eaf'):
    ck=eafpath.split('_')




    [cnt1,anndict1]= elan2json(eafpath,jsonout=False)
    readjson(anndict1)
    print('\n')
    if len(ck[-1])!=13:
        #Errors['filename']=Errors.get('filename',0)+1
        print 'Error Incorrect file name(roll no missing):'+ck[1]
        print 'Rename  the  file in correct format like : L2_<ROLLNO>.eaf'

    errlen=len(Errors)

    if errlen>0:
        print ' TEST FAILED: please correct the errors in YOUR FILE as Errors are displayed above'

    else:
        print 'TEST PASSED'
    return errlen


@begin.start
def checkall(dirpath=r'E:\elan projects\L2\resubmission\*.eaf'):
    global Errors
    import glob
    import csv
    b = open(r'E:\elan projects\L2\resubmission\results.csv', 'w')
    a = csv.writer(b)
    res=[]


    for f in glob.glob(dirpath):
        print f
        roll=f.split('_')[-1][:-4]
        try:
            if checkeaf(f) ==0:
                print roll,':passed'
                res.append([roll,'passed'])

            else:
                print roll,':failed'
                res.append([roll,'failed'])
        except Exception:
                print roll,':failed'
                res.append([roll,'failed:File structure modified\tampered'])
                continue


        Errors.clear()
    a.writerows(res)

    b.close()


