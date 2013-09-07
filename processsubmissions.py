#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      ALI
#
# Created:     06/09/2013
# Copyright:   (c) ALI 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python
import itertools,collections
from nltk.metrics.agreement import AnnotationTask
import elan2json,begin,os,nltk,cPickle,futures
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

def getagreement(task):
    return Agree(kappa=task.kappa(),alpha=task.alpha(),avg_ao=task.avg_Ao())

def json2agreementmatrix(jsonflist):
    from joblib import Memory
    mem = Memory(cachedir=os.path.dirname(jsonflist[0]))
    readjson=mem.cache(json2taskdata.readjson,mmap_mode='r')
    create_task_data= mem.cache(json2taskdata.create_task_data)
    count_occurrances=mem.cache(json2taskdata.count_occurrances)
    count_labels=mem.cache(json2taskdata.count_labels)
    detaildata={}

    annotators=set()
    future_dict={}

    flen=len(jsonflist)
    maxlen=flen

    with futures.ProcessPoolExecutor(max_workers=maxlen/2) as executor:
        while maxlen>1:

            for tpl in list(itertools.combinations(jsonflist,maxlen)):
                annotators=set()
                lectask=[]
                for stditem in tpl:
                    aname=stditem.split('.')[0][3:][-2:]
                    annotators.add(aname)
                    lecdict=readjson(stditem)
                    newlectask= create_task_data(lecdict,task_type='grouped',annotator=aname)
                    label_data=json2taskdata.create_labels_list(newlectask)
                    abscount=count_occurrances(str(label_data))
                    setcount=count_labels(newlectask)
                    lectask=lectask+newlectask

                task=AnnotationTask(data=lectask,distance=nltk.metrics.distance.masi_distance_mod)

                future_dict[executor.submit(getagreement,task)]=frozenset(annotators)




            maxlen=maxlen-1
        for future in futures.as_completed(future_dict):
            if future.exception() is not None:
                print('%r generated an exception: %s' % (url,
                                                     future.exception()))
            else:

                detaildata[future_dict[future]]=future.result()


    cPickle.dump(detaildata,open(os.path.dirname(jsonflist[0])+'\\out.picl','w'))


@begin.start
def main():
    subsdir=r'E:\elan projects\L2\resubmission'
    dstdir=r'passed'
    #copypassedfiles(dstdir,subsdir)
    import glob
    jsonflist=glob.glob(os.path.join(subsdir,dstdir)+'\\'+r'*.379.json')
    json2agreementmatrix(jsonflist)




