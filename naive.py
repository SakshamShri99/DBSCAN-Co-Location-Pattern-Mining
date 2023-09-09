from matplotlib.animation import FuncAnimation
from query import loadData,deleteData,getStudyRegion,createRegionalTable,deleteRegionalTable,getRectangleArea
from visualize import Visualize
from patterns import findPatterns
from constants import THETA,H,STEP,MINA,MAXA,MINL,MAXL
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import itertools
import numpy as np
import time

def parseCSV(path):
    all_instances = []
    sep_instances = {}
    with open(path,mode='r') as file:
        for line in file:
            e,t,log,lat = line.strip().split(' ')
            log = float(log)
            lat = float(lat)
            all_instances.append((e,t,log,lat))
            try:
                sep_instances[e].append((t,log,lat))
            except KeyError:
                sep_instances[e] = [(t,log,lat)]
    return all_instances,sep_instances

all_instances,sep_instances = parseCSV('./data2.txt')

deleteData()
loadData(all_instances)

xmax,ymax,xmin,ymin = getStudyRegion()
box = []
def EnumnerateRectangle():
    count = 0
    total = 0
    print("Bounding Box : ",xmax,ymax,xmin,ymin)
    
    for i in np.arange(xmin,xmax+STEP,STEP):
        for j in np.arange(ymin,ymax+STEP,STEP):
            for k in np.arange(xmin,i+STEP,STEP):
                for l in np.arange(ymin,j+STEP,STEP):
                    if(i > xmax):
                        i = xmax
                    if(j > ymax):
                        j = ymax
                    if(k > i):
                        k = i
                    if(l > j):
                        l = j
                    area = getRectangleArea([i,j,k,l])
                    if(i-k <= MAXL and j-l <= MAXL and i-k >= MINL and j-l >= MINL and area >= MINA and area <= MAXA):
                        events,event_count,event_inst =  createRegionalTable([i,j,k,l])
                        max_patterns,linePoints = findPatterns(events, event_count, H, THETA)
                        deleteRegionalTable()
                        if(max_patterns != []):
                            print([i,j,k,l],max_patterns,end="\n")
                        box.append([i,j,k,l,event_inst,linePoints,max_patterns])
                        count += 1
                    total += 1
    print("Regions Checked : ",count)
    print("Total Regions : ",total)
start = time.time()
EnumnerateRectangle()
end = time.time()
print("Time : ",end-start)
Visualize(all_instances,sep_instances,xmax,ymax,xmin,ymin,box)