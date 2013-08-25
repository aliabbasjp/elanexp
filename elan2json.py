# Script to take .eaf file (which are encoded in XML) dump json

# Input: one  .eaf files
# Output: json file

from xml.etree import ElementTree as ET
import sys
import nltk
import collections,nesteddict

#######################################################################
# Subroutines


def getnonindeptier(name,tiername,type='child',parentdict={}):
        #get non independent tiers: Introduce, Student , Question ...
        #get independent tier type='independent' : Transcript, Comment, Slide
        udict=nesteddict.NestedDict()
        if type=='independent': #transcript,comment etc
            for tr in tiername:
        # Use Xpath to get at annotations, since they're kinda buried
        # Relying on the fact that there is only one of each of these
        # subelements in the scheme.  Possibly a wrong assumption.
                trtext = tr.find('ALIGNABLE_ANNOTATION/ANNOTATION_VALUE').text
                tr_time_ref = tr.find('ALIGNABLE_ANNOTATION').attrib['TIME_SLOT_REF1']
                tr_ann_ref = tr.find('ALIGNABLE_ANNOTATION').attrib['ANNOTATION_ID']

                udict[tr_time_ref][name]=trtext
                udict[tr_ann_ref]=tr_time_ref

        ## make YAML multidimensional dict dic[tr_time_ref][tr_ann_ref]

        if type=='child':
            assert len(parentdict)>0
            tr_dict=parentdict
            for exp in tiername:
                exptext = exp.find('REF_ANNOTATION/ANNOTATION_VALUE').text

                exp_time_ref = tr_dict[exp.find('REF_ANNOTATION').attrib['ANNOTATION_REF']]
                exp_ann_ref = exp.find('REF_ANNOTATION').attrib['ANNOTATION_ID']

                udict[exp_time_ref][name]=exptext
                udict[exp_ann_ref]=exp_time_ref

        return udict

def create_ann_dict(ann_tree):

    # Get our hands on the root of the tree:
    ann = ann_tree.getroot()

    # Get the tiers and the time order
    tiers = ann.getiterator('TIER')
    time = ann.find('TIME_ORDER')
    times=nesteddict.NestedDict()

    for ts in time.getiterator('TIME_SLOT'):
       times[int(ts.attrib['TIME_VALUE'])] = ts.attrib['TIME_SLOT_ID']

    nesteddict.merge(times, dict((times[k], [k]) for k in times) ) #create bidirectional mapping in same dict

    # Find the  annotation tiers, and extract all the
    # annotation nodes
    for tier in tiers:
        vars()[eval("str.lower(tier.attrib['TIER_ID'])")]=eval("tier.getiterator('ANNOTATION')")
        print "tier:"+eval("str.lower(tier.attrib['TIER_ID'])")




    # Loop through the tier to find all of the  annotations
    #  and build a dictionary for each for from
    # time slots (found via TIME_SLOT_REF1) as begining time

    nonparent_tierstoextract='define,question,answer,interaction,summary,equation,introduce,diagram'.split(',')
    parent_tierstoextract={'explain':'topic','story':'storytitle'}
    udict=nesteddict.NestedDict()
    nesteddict.merge(udict,times)

    transcript_dict=getnonindeptier('transcript',vars()['transcript'],'independent')
    #udict.update(transcript_dict)
    udict =nesteddict.merge(udict,transcript_dict)

    for t in nonparent_tierstoextract:
         vars()[t+'_dict']=eval("getnonindeptier(t,eval(t),'child',transcript_dict)")
        # udict.update(vars()[t+'_dict'])
         udict =nesteddict.merge(udict,vars()[t+'_dict'])


    for p,c in parent_tierstoextract.iteritems():
        parent_dict=getnonindeptier(p,vars()[p],'child',transcript_dict)
        child_dict=getnonindeptier(c,vars()[c],'child',parent_dict)
        udict =nesteddict.merge(udict,parent_dict)
        udict =nesteddict.merge(udict,child_dict)

    return[len(transcript_dict),udict]



def main():
    #######################################################################
    # Main script

    # Read in the input files as XML sturctures

    ann_tree1 = ET.parse(sys.argv[1])

    # Output file (for debugging for now)





    # Use the subroutine to get the annotations we're interested in,
    # indexed by the time stamp of the start of the region they're associated
    # with.

    [cnt1,anndict1]=create_ann_dict(ann_tree1)
    import json
    outfile1=open(sys.argv[1]+"."+str(cnt1/2)+ '.json','w')
    json.dump(anndict1,outfile1,indent=4)




    exit()


if __name__ == '__main__':
    main()
