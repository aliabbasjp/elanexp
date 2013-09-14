"""
.. module:: processsubmissions.py
   :description:
   :date: 09/09/2013
   :license: MIT License

.. moduleauthor:: Aliabbas Petiwala <aliabbas@iitb.ac.in>

"""
#!/usr/bin/env python
import itertools,collections
from joblib import Memory
from nltk.metrics.agreement import AnnotationTask
import elan2json,begin,os,nltk,cPickle,futures,yaml
import json2taskdata
rolls=['100020003',
 '100020006',
 '100020016',
 '100020021',
 '100020023',
 '100020026',
 '100020030',
 '100020031',
 '100020032',
 '100020033',
 '100020034',
 '100020034',
 '100020037',
 '100020039',
 '100020044',
 '100020045',
 '100020046',
 '100020050',
 '100020051',
 '100020054',
 '100020056',
 '100020057',
 '100020058',
 '100020062']
  ##r'E:\elan projects\L2\resubmission',r'L2_\d{9}\.eaf$')
Agree = collections.namedtuple('Agree', ['kappa', 'alpha','avg_ao'], verbose=True)


def copypassedfiles(reldstdir='',srcdir=r'E:\elan projects\L2\resubmission',rollnos=None):
    """converts the shortlisted eaf files to json and copies to a destination dir

        Args:
           reldstdir (str):  destination directory to pass the correct json files
           rollnos (list): list of passed rollnos (correctly annotated files)

        Returns:
          list of files with full json path pointing to destination directory

        """
    rollnos=rollnos or None or rolls
    dstdir=os.path.join(srcdir,reldstdir)
    pattern= "|".join("L2_%s\.eaf$" % w for w in rolls)

    import regglob
    res=regglob.reglob(srcdir,pattern)
    if dstdir is not None and reldstdir!='':
        if not os.path.exists(dstdir):
            os.makedirs(dstdir)
        import shutil
        for i in res :
            shutil.copy(i, dstdir)

        elan2json.elan2json(None,dirpath=dstdir+'\\*.eaf')

        return map(lambda f: os.path.join('\\'.join(f.split('\\')[:-1]),reldstdir+'\\'+f.split('\\')[-1]),res)

    return res
def csvdump(dic,fil):
    import csv

    f = csv.writer(fil)

        # Write CSV Header, If you dont need that, remove this line
    f.writerow(["annotators", "alpha", "kappa", "AvgObs"])

    for k,v in dic.items():
        f.writerow([','.join(list(k)),v[0],v[1],v[2]])
    fil.close()


def getagreement(tpl,datadir):
    """Get agreement values for annotators in the :data:'tpl' list

    Args:
       tpl (list):  combination group of annotators
       datadir (str): Cache data directory used by joblib

    Returns:
       namedtuple defined as ``Agree = collections.namedtuple('Agree', ['kappa', 'alpha','avg_ao'], verbose=True)``
    """

    mem = Memory(cachedir=datadir)
    readjson=mem.cache(json2taskdata.readjson,mmap_mode='r')
    create_task_data= mem.cache(json2taskdata.create_task_data)
    count_occurrances=mem.cache(json2taskdata.count_occurrances)
    count_labels=mem.cache(json2taskdata.count_labels)

    annotators=set()
    lectask=[]
    #-------------------------------------------------------------------------------
    # for each annotator in group tpl
    #-------------------------------------------------------------------------------

    for stditem in tpl:
        aname=stditem.split('.')[0][3:][-2:]
        annotators.add(aname)
        lecdict=readjson(stditem)
        newlectask= create_task_data(lecdict,task_type='grouped',annotator=aname)
##        label_data=json2taskdata.create_labels_list(newlectask)
##        abscount=count_occurrances(str(label_data))
##        setcount=count_labels(newlectask)
        lectask=lectask+newlectask

    task=AnnotationTask(data=lectask,distance=nltk.metrics.distance.masi_distance_mod)

    return  {frozenset(annotators): Agree(task.kappa(),task.alpha(),task.avg_Ao())}

def json2agreementmatrix(jsonflist,start=2,maxlen=0):
    """ Multi process function to convert json to
    agreement values (alpha,kappa,Avg Observed agreement)

        Args:
           jsonflist (list):  list of json filenames.
           start (int): combination group size to begin with.
           maxlen(int): maximum count starting from :data:'start'


        Kwargs:
           state (bool): Current state to be in.

        Returns:
           A dict mapping annotator combination to agreement values then pickled.

        Raises:
           Future.Exception


        """


    future_list=[]
    detaildata={}

    flen=len(jsonflist)


    assert start+maxlen-2<=flen



    with futures.ProcessPoolExecutor() as executor:
        for cnt in range(start,start+maxlen+1):
            for tpl in list(itertools.combinations(jsonflist,cnt)):
                future_list.append(executor.submit(getagreement,tpl,os.path.dirname(jsonflist[0])))


        for future in futures.as_completed(future_list):
            if future.exception() is not None:
                print('%r generated an exception: %s' % (future,
                                                     future.exception()))
            else:

                detaildata.update( future.result())


    cPickle.dump(detaildata,open(os.path.dirname(jsonflist[0])+'\\'+str(start)+'-'+str(start+maxlen)+'out.picl','w'))
    yaml.dump(detaildata,open(os.path.dirname(jsonflist[0])+'\\'+str(start)+'-'+str(start+maxlen)+'out.yaml','w'))
    csvdump(detaildata,open(os.path.dirname(jsonflist[0])+'\\'+str(start)+'-'+str(start+maxlen)+'out.csv','w'))
    print "Dumped output"
    return detaildata


@begin.start
def main():
    subsdir=r'E:\elan projects\L2\resubmission'
    dstdir=os.path.join(subsdir,r'passed')
    #copypassedfiles(dstdir,subsdir)
    import glob
    jsonflist=glob.glob(dstdir+'\\'+r'*.379.json')
    mem = Memory(cachedir=dstdir)
    json2agreementmatrix_cached=mem.cache(json2agreementmatrix)

    c=json2agreementmatrix_cached(jsonflist)
    print c






