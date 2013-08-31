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
import nltk
from nltk.metrics.agreement import AnnotationTask
import json,sys,begin
import datadiff
tagslist="""anecdote
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
tags=set(tagslist)
# Sub-routine to create annotation task format required by
# nltk.metrics.agreement: This is a list of tuples with the following
# elements: annotator, word, label where we will be representing the
# words with their initial time stamps


def set2groupedset(tagset):
    grpset=set()
    for t in tagset:
        def s(t):
            return{
        'anecdote':'story',
        'example':'story',
        'demo':'story',
        'preview':'summary',
		'generalreview':'summary',
		'futurepreview':'summary',
		'postsummary':'summary',
		'focusinginformation':'question',
		'stimulatingthought':'question',
#        'answer':'answer'
		'aims&objectives':'introduce',
		'motivation':'introduce',
		'student question':'interaction',
		'student answer':'interaction',
		'other':'interaction',
#		'diagram':'visual',
#		'equation':'visual',
		'describing&interpreting':'explain',
		'recounting':'explain',
		'reporting':'explain'
#		'define':'define'
                }.get(t, t)

        grpset.add(s(t))
    return frozenset(grpset)



def filteredset(tagset,allowed):
    grpset=set()
    for t in tagset:
        if t in allowed:
            grpset.add(t)
    return frozenset(grpset)


def create_task_data(elan_dict,task_type='all',allowed='define,describing&interpreting',skipped='',annotator='annotator1'):
# This sub-routine will take in the  annotation dictionary
# for one annotator and produce a list of tuples for just
# that annotator.  It takes two additional arguments: the label
# to use for the annotator and the task_type, which determines
# what we are measuring agreement over.

# Task_type controls what we put into the agreement data set:
#  all : one entry per word, with labels (18 categories?)
#  grouped : Only parent group representing the child labels
#  filtered : A limited set of tags which would be the only ones that will be extracted
#  filtered-grouped : same as filtered but also grouped

#  filtering rules
#  allowed:  if string CSV then extract only allowed tags, else extract all tags(same as to all)
#  skipped: allow all except the ones to skip listed in CSV

    skipped=skipped.split(',')

    # The return value will be a list of tuples.
    if type(allowed)==str:
        allowed=set(allowed.split(','))
    else:
        allowed=set(tags)
    if len(skipped)>1:
        allowed=set(tags)
        allowed=allowed-set(skipped)
        allowed=set(allowed).difference(set(skipped))

    task_data = []




    for (k,v) in elan_dict.iteritems():
        if task_type=='all':
            task_data.append([annotator,k,v])
        elif task_type=='grouped':
            task_data.append([annotator,k,set2groupedset(v)])
        elif task_type=='filtered':
            task_data.append([annotator,k,filteredset(v,allowed)])
        elif task_type=='filtered-grouped':
             task_data.append([annotator,k,set2groupedset(filteredset(v,allowed))])
        else:
            raise Exception( "Wrong option <tasktype>" )




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
        return [errorlist,frozenset(assigned)]


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

##27,49


@begin.start
def main():
    #print datadiff.diff_dict(readjson('E:\elan projects\L2\submissions\extracted\L2_100020027.eaf.379.json'),readjson('E:\elan projects\L2\submissions\extracted\L2_100020049.eaf.379.json'))
    s1=readjson('E:\elan projects\L2\submissions\extracted\L2_100020027.eaf.379.json')
    s2=readjson('E:\elan projects\L2\submissions\extracted\L2_100020049.eaf.379.json')
    #s2=readjson('E:\elan projects\L2\L2v1f_DIP.eaf.379.json')
    #s2=readjson('E:\elan projects\L2\L2v1_PRI.eaf.379.json')
    s1_data= create_task_data(s1,task_type='grouped',allowed='define',annotator='s1')
    s2_data=create_task_data(s2,task_type='grouped',allowed='define',annotator='s2')
    task=AnnotationTask(data=s1_data+s2_data,distance=nltk.metrics.distance.masi_distance_mod)
  #  print "Observed Agreement:{0}".format( task.Ao('s1','s2'))
    print "Kappa:{0}".format(task.kappa())
    print "Alpha:{0}".format(task.alpha())
    print "Observed Avg Agreement over all:{0}".format(task.avg_Ao())







