#-------------------------------------------------------------------------------
# Name:        json to task data
# Purpose:
#
# Author:      ALI
#
# Created:     25/08/2013
# Copyright:   (c) ALI 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python
import json,sys,begin
import datadiff
tags="""anecdote
example
demo
preview
GeneralReview
FuturePreview
postsummary
FocusingInformation
StimulatingThought
answer
Aims&Objectives
motivation
Student Question
Student Answer
Other
diagram
equation
Describing&Interpreting
Recounting
Reporting
define
""".lower().splitlines()
tags=set(tags)
# Sub-routine to create annotation task format required by
# nltk.metrics.agreement: This is a list of tuples with the following
# elements: annotator, word, label where we will be representing the
# words with their initial time stamps

# This sub-routine will take in the muc annotation dictionary
# for one annotator and produce a list of tuples for just
# that annotator.  It takes two additional arguments: the label
# to use for the annotator and the task_type, which determines
# what we are measuring agreement over.

# Task_type controls what we put into the agreement data set:
#  all : one entry per word, with labels
#  binary : one entry per word, not distinguishing labels (i.e.,
#           replacing all non-'NONE' entries with 'ENTITY')
#  labels : only entries with labels

def create_task_data(muc_dict,annotator,task_type):

    # The return value will be a list of tuples.
    task_data = []

    # Step through the input dictionary one key at a time:
    # ~*~

        # If the task_type is 'all' or 'labels', then store
        # the value muc_dict[key] as the label to return.
        # ~*~

        # If the task type is 'binary', the label to return
        # should be 'NONE' (if that's what it is) or 'ENTITY'
        # otherwise.
        # ~*~

        # Create the task item, which is a triple of the form
        # [annotator, key, label]
        # ~*~

        # Now decide whether to add the task item to the list
        # of task_data.  If the task_type is 'all' or 'binary',
        # then add it.  If it's 'labels', then add it only if
        # the label isn't 'NONE'.
        # ~*~


    return task_data

# Subroutine for creating a list of annotation labels ordered
# by timestamp (but without the time stamps).  This is to create
# the input required by nltk.metrics.ConfusionMatrix.  Assume
# that ann_dict has timestamps (integers) as the keys.

def create_labels_list(muc_dict):

    labels_list = []

    # Get the list of keys from muc_dict, and sort them
    # ~*~

    # For each key in that list (in order) add the corresponding
    # value in muc_dict to labels_list
    # ~*~

    return labels_list

# Subroutine to count use of each label by an annotator
# Returns a dictionary mapping labels to their counts in
# the input annotation dictionary.

def count_labels(ann_dict):

    counts = {}

    # For each item in ann_dict, check whether the value
    # of that item is already a key in counts.  If so, add
    # 1 to it's value.  If not, create an entry in counts for
    # it, with value 1.  (This is similar to freq.py from Lab 4.)
    # ~*~

    return counts

def getdict2set(d):

        assigned=set()

        errorlist=[]

        for (k,v) in d.iteritems():
            if k =='explain'or k=='summary' or k=='introduce' or k=='story' or k=='question' or k=='interaction':
                if  set([str(v).lower()]).issubset(tags): #store only value for multivalued tags
                    assigned.add(v.lower())
                else:
                    errorlist.append('Error: Multivalued tag <{0}> is assigned a wrong value <{1}>'.format(str(k),str(v)))

            elif k!='storytitle' and k!='topic': #store tag for single valued tags
                 if  set([str(k)]).issubset(tags):
                    assigned.add(k.lower())
                 else:
                    errorlist.append('Error: Multivalued tag {0} is incorrect and has value {1}'.format(str(k),str(v)))



            #if  len(assigned)>0:
                #print assigned
##                if not (assigned.issubset(tags)):
##                    print 'Error:Wrong key:{0} for value:{1} in dict'.format(k,v)

        assert len( assigned)<18
        return [errorlist,assigned]


begin.subcommand
def readjson(eafpath='E:\elan projects\L1\L1v1_DIP.eaf.319.json',verbose='no'):


    #jsoneaf:json dump for eaf file#

    jsoneaf=json.load(open(eafpath))
    import collections
    d=collections.OrderedDict()
    for (k,v) in jsoneaf.iteritems():
        savtr,savsli="",""


        if v.has_key('transcript'):
            savtr=v['transcript']
            del v['transcript']
        if v.has_key('slide'):
            savsli=v['slide']
            del v['slide']




        [errors,d[k]]=getdict2set(v)
        if verbose=='yes':
            import nesteddict
            savdic={k:[savtr,savsli]}
            d[k]=nesteddict.merge(savdic,{k:d[k]})

        if len(errors)>0:
            print "At time {0}: {1}".format(k,errors)



    #print d
    return d



@begin.start
def main():
    print datadiff.diff_dict(readjson('E:\elan projects\L2\submissions\extracted\L2_100020027.eaf.379.json'),readjson('E:\elan projects\L2\submissions\extracted\L2_100020049.eaf.379.json'))




