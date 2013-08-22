# Script to take .eaf files (which are encoded in XML) and
# extract the annotations that we are interested in, compare
# for differences, and calculate kappa scores.

# Input: two .eaf files
# Output: text file with differences noted, kappa scores
#         confusion matrix, total Ns for each annotation type

from xml.etree import ElementTree as ET
import sys
import nltk
import collections,nesteddict

#######################################################################
# Subroutines

# Sub routine to create dictionaries of annotations from tree
# representation of .eaf files.  Creating this as a subroutine because
# We need to do it for both of the files and don't want to repeat that
# code. Input is annotation tree, output is a pair (list of two elements):
#
# [ word_count, muc_dict ]
#
# Where word_count is an integer recording how many words there are
# total in the document and muc_dict is a dictionary mapping the
# initial time stamp of each word to the annotation on the MUC-7 tier,
# or 'NONE' if there was no annotation.


   ##tr_dict.update( dict((d[k], k) for k in tr_dict) ) #create bidirectional mapping in same dict
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

                udict[tr_time_ref][name][tr_ann_ref]=trtext
                udict[tr_ann_ref]=tr_time_ref

        ## make YAML multidimensional dict dic[tr_time_ref][tr_ann_ref]

        if type=='child':
            assert len(parentdict)>0
            tr_dict=parentdict
            for exp in tiername:
                exptext = exp.find('REF_ANNOTATION/ANNOTATION_VALUE').text

                exp_time_ref = tr_dict[exp.find('REF_ANNOTATION').attrib['ANNOTATION_REF']]
                exp_ann_ref = exp.find('REF_ANNOTATION').attrib['ANNOTATION_ID']

                udict[exp_time_ref][name][exp_ann_ref]=exptext
                udict[exp_ann_ref]=exp_time_ref

        return udict

def create_ann_dict(ann_tree):

    # Get our hands on the root of the tree:
    ann = ann_tree.getroot()

    # Get the tiers and the time order
    tiers = ann.getiterator('TIER')
    time = ann.find('TIME_ORDER')
    times=nesteddict.NestedDict()

##    # Add entries with value 'NONE' for all of the time slots corresponding
##    # to words that weren't annotated:
##
    for ts in time.getiterator('TIME_SLOT'):
       times[int(ts.attrib['TIME_VALUE'])] = ts.attrib['TIME_SLOT_ID']
##
 #   nesteddict.merge(times, dict((times[k], k) for k in times) ) #create bidirectional mapping in same dict
##
##
##    return [times,trtext]


    # Find the word & MUC-7 annotation tiers, and extract all the
    # annotation nodes from those tiers.  We need the words so we
    # know how many annotation targets there were.

    for tier in tiers:
        vars()[eval("str.lower(tier.attrib['TIER_ID'])")]=eval("tier.getiterator('ANNOTATION')")
        print "tier:"+eval("str.lower(tier.attrib['TIER_ID'])")
##        if tier.attrib['TIER_ID'] == 'Transcript':
##            transcript = tier.getiterator('ANNOTATION')
##        if tier.attrib['TIER_ID'] == 'Explain':
##            explain = tier.getiterator('ANNOTATION')
##        if tier.attrib['TIER_ID'] == 'Topic':
##            topic = tier.getiterator('ANNOTATION')

##    assert len(explain)==len(topic)
##    assert len(story)==len(storytitle)



    # Loop through the tier to find all of the  annotations
    #  and build a dictionary for each for from
    # time slots (found via TIME_SLOT_REF1) as begining time
  #  tr_dict,tr_text,exp_dict,exp_text,top_dict,top_text,times= [{} for _ in range(7)] #create n empty dictionaries

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
##        udict.update(parent_dict)
##        udict.update(child_dict)
        udict =nesteddict.merge(udict,parent_dict)
        udict =nesteddict.merge(udict,child_dict)




    return[len(transcript_dict),udict]




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


#######################################################################
# Main script

# Read in the input files as XML sturctures

ann_tree1 = ET.parse(sys.argv[1])
ann_tree2 = ET.parse(sys.argv[2])

# Output file (for debugging for now)

outfile = open('op.txt','w')
outfileyaml1=open(sys.argv[1]+'.yaml','w')

outfileyaml2=open(sys.argv[2]+'.yaml','w')

# Use the subroutine to get the annotations we're interested in,
# indexed by the time stamp of the start of the region they're associated
# with.

import pprint
anndict=create_ann_dict(ann_tree1)[1]
import json
json.dump(anndict,outfile,indent=4)

exit()
import pyaml
anndata1= pyaml.dump(create_ann_dict(ann_tree1)[1])
anndata2=pyaml.dump(create_ann_dict(ann_tree2)[1])

outfileyaml1.write(anndata1)
outfileyaml2.write(anndata2)



exit()
# Check that we have the same number of words in each file:

if words1 != words2:
    sys.exit("The two files have different word counts. Something's wrong.")
else:
    print "Success! There are " + str(words1) + " words."

#######################################################################
# Check for agreement on tags only (looking only at ones that
# both chose as some kind of named entity):

# Initialize the muc_task variable to an empty list.
muc_task = []

# Use the subroutine create_task_data to create two lists, one for
# each annotator, with the 'labels' option.
# ~*~


# Loop through one annotator's tuples:
# ~*~

    # For each item, loop through the other annotator's tuples.
    # ~*~

        # If we find one with the same key, add the tuples
        # from both annotators to the muc_task list.
        # ~*~


# Write total number of words annotated as named entities by both
# annotators to the output file:
outfile.write("There are " + str(len(muc_task)/2) + " words annotated as named entities by both annotators.\n\n")

# Create the Annotation task out of the data in muc_task
# ~*~

# Write text explaining what value is coming next:
outfile.write("IAA calculated as Cohen's kappa on their choices of entity type: ")

# Calculate and write the kappa value
# ~*~

# Write text explaining what value is coming next:
outfile.write("IAA calculated as Krippendorff's alpha on their choices of entity type: ")

# Calculate and write the alpha value
# ~*~


#######################################################################
# Check for agreement on whether words are part of named entities,
# regardless of labels:

# Use the subroutine create_task_data to create two lists, one for
# each annotator, with the 'binary' option.
# ~*~

# Concatenate the two to make one big data list, stored again in muc_task:
# ~*~

# Write total number of words to be annotated to the output file:
outfile.write("There were " + str(len(muc_task)/2) + " words that could be annotated total.\n\n")

# Create the Annotation task out of the data in muc_task
# ~*~

# Write text explaining what value is coming next:
outfile.write("Agreement between the annotators on whether a word belonged to a named entity or not, calculated as Cohen's kappa: ")

# Calculate and write the kappa value
# ~*~

# Write text explaining what value is coming next:
outfile.write("Agreement between the annotators on whether a word belonged to a named entity or not, calculated as Krippendorff's alpha: ")

# Calculate and write the alpha value
# ~*~


#######################################################################
# Check for overall agreement:

# Use the subroutine create_task_data to create two lists, one for
# each annotator, with the 'all' option.
# ~*~

# Concatenate the two to make one big data list, store in muc_task again:
# ~*~

# Create the Annotation task out of the data in muc_task
# ~*~

# Write text explaining what value is coming next:
outfile.write("Agreement between the annotators on whether a word belonged to a named entity or not and what entitty type, calculated as Cohen's kappa: ")

# Calculate and write the kappa value
# ~*~

# Write text explaining what value is coming next:
outfile.write("Agreement between the annotators on whether a word belonged to a named entity or not and what entitty type, calculated as Krippendorff's alpha: ")

# Calculate and write the alpha value
# ~*~

#######################################################################
# Print confusion matrix
# nltk.metrics.ConfusionMatrix takes in two lists of labels (ordered
# so that the nth members of the list correspond to each other).

# Use create_label_list() defined above to get the list of labels for each
# annotator
# ~*~

# Use nltk.metrics.ConfusionMatrix to calculate the confusion matrix
# and print it to the output file.
# ~*~


#######################################################################
# Print total numbers of each label type from each annotator:

# Use count_labels() defined above to get counts for each annotator
# of how many times they used each label.
# ~*~

# Print these, along with some explanatory text, to the output file.
# ~*~



#######################################################################
# Print list of diffs

# Write text explaining what is coming next.
outfile.write("List of diffs.\n\n")

# Get the list of tuples from create_task_data for each
# annotator, with the 'all' tag.  (These may still be available
# from above.)
# ~*~

# Sort these lists by item identifier ('key').
# ~*~

# Step through them in tandem (one for loop, with one counter
# used to index both lists).  For any pair where the label doesn't
# match, print both items to the output file.
# ~*~








