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

from xml.etree import ElementTree as ET
import sys
import nltk
import collections,nesteddict

#######################################################################
# Subroutines

def getnonindeptier(name,tiername,times,type='child',parentdict={}):
        #get non independent tiers: Introduce, Student , Question ...
        #get independent tier type='independent' : Transcript, Comment, Slide
        udict=nesteddict.NestedDict()
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
            print name+' : a child tier is empty'

        return udict

def create_ann_dict(ann_tree,independent_tiers,nonparent_tierstoextract,parent_tierstoextract):


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
    for tier in tiers:
        vars()[eval("str.lower(tier.attrib['TIER_ID'])")]=eval("tier.getiterator('ANNOTATION')")
        print "tier:"+eval("str.lower(tier.attrib['TIER_ID'])")

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
            print i +" : an Independent Tier is empty...."

    for t in nonparent_tierstoextract:
        if len(eval(t)) >0:
             vars()[t+'_dict']=eval("getnonindeptier(t,eval(t),times,'child',transcript_dict)")
            # udict.update(vars()[t+'_dict'])
             udict =nesteddict.merge(udict,vars()[t+'_dict'])
        else:
            print t +" a non parent tier Is empty...."

    for p,c in parent_tierstoextract.iteritems():
        parent_len=len(eval(p))
        child_len=len(eval(c))
        if parent_len!=child_len:
            print " Warning Mismatch of parent-child length in  dependent tiers:",p,',',c

        if  parent_len>0 or child_len >0:
            parent_dict=getnonindeptier(p,vars()[p],times,'child',vars()['transcript_dict'])
            child_dict=getnonindeptier(c,vars()[c],times,'child',parent_dict)
            udict =nesteddict.merge(udict,parent_dict)
            udict =nesteddict.merge(udict,child_dict)
        else:
            print 'Missing parent or child:',p,',',c

    ##REMOVE the timing and annotation labels ts1,a1
    for k in udict.keys():
        if k.startswith('ts') or k.startswith('a'):
            del udict[k]

    udict=collections.OrderedDict(sorted(udict.items()))

    return[len(vars()['transcript_dict'])/2,udict]

def main():
    #######################################################################
    # Main script

    # Read in the input files as XML sturctures

    ann_tree1 = ET.parse(sys.argv[1])

    # Output file (for debugging for now)

    # Use the subroutine to get the annotations we're interested in,
    # indexed by the time stamp of the start of the region they're associated
    # with.
    independent_tiers='transcript,comment,slide'.split(',')
    nonparent_tierstoextract='define,question,answer,interaction,summary,equation,introduce,diagram'.split(',')
    parent_tierstoextract={'explain':'topic','story':'storytitle'}

    [cnt1,anndict1]=create_ann_dict(ann_tree1,independent_tiers,nonparent_tierstoextract,parent_tierstoextract)
    import json

    outfile1=open(sys.argv[1]+"."+str(cnt1)+ '.json','w')
    json.dump(anndict1,outfile1,indent=4)

    exit()


if __name__ == '__main__':
    main()
