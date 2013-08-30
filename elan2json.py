# Script to take .eaf file (which are encoded in XML) and convert to json dump
#-------------------------------------------------------------------------------
# Name:        elan2json.py
# Purpose:
#
# Author:      Aliabbas Petiwala, IITB
#
# Created:     28/08/2013
# Copyright:   (c)  Aliabbas Petiwala 2013
# Licence:     GNU GPLv3
#-------------------------------------------------------------------------------
#!/usr/bin/env python

# Input: one  .eaf files
# Output: json file
from __future__ import print_function

from xml.etree import ElementTree as ET
import begin
import nltk
import collections,nesteddict

#######################################################################
# Subroutines

def getnonindeptier(name,tiername,times,type='child',parentdict={}):
        #get non independent tiers: Introduce, Student , Question ...
        #get independent tier type='independent' : Transcript, Comment, Slide
        udict=nesteddict.NestedDict()
        #print 'tiers:::::::::::::::::::::'+str(tiername)
        if type=='independent': #transcript,comment etc
            for tr in tiername:
        # Use Xpath to get at annotations, since they're kinda buried
        # Relying on the fact that there is only one of each of these
        # subelements in the scheme.  Possibly a wrong assumption.
                trtext = tr.find('ALIGNABLE_ANNOTATION/ANNOTATION_VALUE').text
                tr_time_ref_beg = times[tr.find('ALIGNABLE_ANNOTATION').attrib['TIME_SLOT_REF1']]
                tr_time_ref_end = times[tr.find('ALIGNABLE_ANNOTATION').attrib['TIME_SLOT_REF2']]
                tr_ann_ref = tr.find('ALIGNABLE_ANNOTATION').attrib['ANNOTATION_ID']
##                mutabledict = {'beg':tr_time_ref_beg,'end':tr_time_ref_end}
##                intervals=frozenset(mutabledict.items())
                intervals=(tr_time_ref_beg,tr_time_ref_end)


                udict[tr_time_ref_beg][name]=[tr_time_ref_end, trtext]
                udict[tr_ann_ref]=tr_time_ref_beg

        ## make YAML multidimensional dict dic[tr_time_ref][tr_ann_ref]

        if type=='child':
            if len(parentdict)>0:
                tr_dict=parentdict
                for exp in tiername:
                    exptext = exp.find('REF_ANNOTATION/ANNOTATION_VALUE').text

                    exp_time_ref = tr_dict[exp.find('REF_ANNOTATION').attrib['ANNOTATION_REF']]
                    exp_ann_ref = exp.find('REF_ANNOTATION').attrib['ANNOTATION_ID']

                    udict[exp_time_ref][name]=exptext
                    udict[exp_ann_ref]=exp_time_ref

        return udict

def elan2dict(eafpath,independent_tiers,nonparent_tierstoextract,parent_tierstoextract):
    ann_tree = ET.parse(eafpath)

    # Get our hands on the root of the tree:
    ann = ann_tree.getroot()

    # Get the tiers and the time order
    tiers = ann.getiterator('TIER')
    time = ann.find('TIME_ORDER')
    times=nesteddict.NestedDict()

    for ts in time.getiterator('TIME_SLOT'):
       times[ts.attrib['TIME_SLOT_ID']] = ts.attrib['TIME_VALUE']

#    nesteddict.merge(times, dict((times[k], [k]) for k in times) ) #create bidirectional mapping in same dict

    # Find the  annotation tiers, and extract all the
    # annotation nodes and store it in a variable with its name equal to tier name
    print('tiers found:')
    for tier in tiers:
        vars()[tier.attrib['TIER_ID'].lower()]=tier.getiterator('ANNOTATION')
        #print(str(eval("str.lower(tier.attrib['TIER_ID'])")),end=', ')
        print( '{0}'.format(tier.attrib['TIER_ID'].lower()), end=',')


    # Loop through the tier to find all of the  annotations
    #  and build a dictionary for each for from
    # time slots (found via TIME_SLOT_REF1) as begining time
    udict=nesteddict.NestedDict()

    nesteddict.merge(udict,times)


    for i in independent_tiers:
        if len(eval(i)) >0:
            vars()[i+'_dict']=eval("getnonindeptier(i,eval(i),times,'independent')")
            udict =nesteddict.merge(udict,vars()[i+'_dict'])
        else:
            print (i +" : an Independent Tier is empty....")

    for t in nonparent_tierstoextract:
        if len(eval(t)) >0:
             vars()[t+'_dict']=eval("getnonindeptier(t,eval(t),times,'child',transcript_dict)")
            # udict.update(vars()[t+'_dict'])
             udict =nesteddict.merge(udict,vars()[t+'_dict'])
        else:
            print( t +" a non parent tier Is empty....")

    for p,c in parent_tierstoextract.iteritems():
        parent_len=len(eval(p))
        child_len=len(eval(c))
        if parent_len!=child_len:
            print( " Warning Mismatch of parent-child length in  dependent tiers:",p,',',c)

        if  parent_len>0 or child_len >0:
            parent_dict=getnonindeptier(p,vars()[p],times,'child',vars()['transcript_dict'])
            child_dict=getnonindeptier(c,vars()[c],times,'child',parent_dict)
            udict =nesteddict.merge(udict,parent_dict)
            udict =nesteddict.merge(udict,child_dict)
        else:
            print( 'Missing parent or child:',p,',',c)

    ##REMOVE the timing and annotation labels ts1,a1
    for k in udict.keys():
        if k.startswith('ts') or k.startswith('a'):
            del udict[k]

    udict=collections.OrderedDict(sorted(udict.items()))

    return[len(vars()[independent_tiers[0]+'_dict'])/2,udict]  #return with the count of the first independent tier

def str2dict(contents):
    if contents=='#': ## # means empty
        return {}
    else:

        items = contents.split(',') # each individual item looks like key:value
        pairs = [item.split(':',1) for item in items] # ("key","value"), both strings
        d = dict((k,v) for (k,v) in pairs) # create new dict
        return d

@begin.start
def elan2json(eafpath='E:\elan projects\L1\L1v1_DIP.eaf',independent_tiers='transcript,comment,slide',nonparent_tiers='define,question,answer,interaction,summary,equation,introduce,diagram',parent_tiers='explain:topic,story:storytitle',skip='slide,comment',jsonout=True, dirpath=None):


    independent_tiers=independent_tiers.split(',')
    for s in skip.split(','):
        independent_tiers.remove(s)


    nonparent_tiers=nonparent_tiers.split(',')
    parent_tiers=str2dict(parent_tiers)
    if dirpath is None:
        [cnt1,anndict1]=elan2dict(eafpath,independent_tiers,nonparent_tiers,parent_tiers)
        if jsonout:
            import json

            outfile1=open(eafpath+"."+str(cnt1)+ '.json','w')
            json.dump(anndict1,outfile1,indent=4)
            print( 'output:'+eafpath+"."+str(cnt1)+ '.json')
        return [cnt1,anndict1]

    else:
        import glob,random
        import json
        print( 'Dumping JSON for path:'+dirpath)
        fils=glob.glob(dirpath)
        random.shuffle(fils)
        for eafpath in fils:
            print('file='+eafpath)
            [cnt1,anndict1]=elan2dict(eafpath,independent_tiers,nonparent_tiers,parent_tiers)
            outfile1=open(eafpath+"."+str(cnt1)+ '.json','w')
            json.dump(anndict1,outfile1,indent=4)
            print( 'output:'+eafpath+"."+str(cnt1)+ '.json')


def main():
    #######################################################################
    # Main script

    # Read in the input files as XML sturctures

    # Output file (for debugging for now)

    # Use the subroutine to get the annotations we're interested in,
    # indexed by the time stamp of the start of the region they're associated
    # with.
    independent_tiers='transcript,comment,slide'.split(',')
    nonparent_tierstoextract='define,question,answer,interaction,summary,equation,introduce,diagram'.split(',')
    parent_tierstoextract={'explain':'topic','story':'storytitle'}
    begin.start
    elan2json(independent_tiers='transcript')



##if __name__ == '__main__':
##    main()
