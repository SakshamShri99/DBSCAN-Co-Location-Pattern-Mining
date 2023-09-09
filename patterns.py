import csv
from query import loadData,deleteData,spatialJoin,generateInstanceTable
import itertools

def interestMeasure(table,event_count):
    IM = {}
    for key,value in table.items():
        prod = 1
        for e in key:
            prod *= event_count[e]
        IM[key] = float(len(value))/prod
    return IM

def findPatterns(events,event_count,h,threshold):
    all_patterns = []
    exclude = []
    table = {}
    IM = {}
    previous = []
    max_patterns = []
    linePoints = []
    for i in range(2,len(events)+1):
        if(i == 2):
            table,linePoints = spatialJoin(h,events)
            IM = interestMeasure(table,event_count)
        else:
            table = generateInstanceTable(h, i,table.keys(), exclude)
            IM = interestMeasure(table,event_count)
        
        current = []
        for col,im in IM.items():
            if(im < threshold):
                exclude.append(set([*col]))
            else:
                current.append(col)

        for p in previous:
            flag = False
            for c in current:
                if(set([*p]).issubset(set([*c]))):
                    flag = True
                    break
            if(not flag):
                max_patterns.append(p)
        previous = current
        if(table == {}):
            break

    for p in previous:
        max_patterns.append(p)

    return max_patterns,linePoints