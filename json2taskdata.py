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
import naturalsort,json,sys

def main():
    pass

if __name__ == '__main__':
    main()



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

def readjson(jsoneaf):
    #jsoneaf:json dump for eaf file#

##    def filterout(j):
##        if 'ts' not in j and 'a' not in j:
##         return True
##
##    beg_times=filter(filterout, jsoneaf.keys())
##    beg_times.sort(key=naturalsort.natural_keys)
##
    newlist=[]
    cnt=0
    while (jsoneaf.has_key('ts'+str(cnt))):
        if len( jsoneaf['ts'+str(cnt)])>1:
            newlist.append(jsoneaf['ts'+str(cnt)])
        cnt=cnt+1
        print cnt

    print newlist

def main():
    readjson(json.load(open(sys.argv[1])))


if __name__ == '__main__':
    main()


