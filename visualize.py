from matplotlib.animation import FuncAnimation,FFMpegWriter
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.offsetbox import AnchoredText
import numpy as np
from constants import THETA,H,STEP,MINA,MAXA

fig,(ax1,ax2) = plt.subplots(1,2,figsize=(14,7))
rect = patches.Rectangle((0,0),0,0,linewidth=1,edgecolor='r',facecolor='none')

def Visualize(all_instances,sep_instances,xmax,ymax,xmin,ymin,box):
    for inst in sep_instances.values():
        X = [d[1] for d in inst]
        Y = [d[2] for d in inst]
        ax1.scatter(X,Y)
    ax1.legend(sep_instances.keys(),bbox_to_anchor=(-0.1,1),bbox_transform=ax1.transAxes)
    bbox1 = patches.Rectangle((xmin,ymin),xmax-xmin,ymax-ymin,linewidth=1,edgecolor='g',facecolor='none',linestyle='--')
    ax1.add_patch(bbox1)
    ax1.set_title("Study Region")
    ani = FuncAnimation(fig,anim,init_func=init,frames=len(box),fargs=(box,),interval=1,repeat=False)
    # plt.show()
    FFwriter = FFMpegWriter(fps=5)
    ani.save('Algo.mp4', writer = FFwriter)

def init():
    ax1.add_patch(rect)
    return rect
def anim(i,box):
    rect.set_width(box[i][0]-box[i][2])
    rect.set_height(box[i][1]-box[i][3])
    rect.set_xy((box[i][2],box[i][3]))
    ax2.cla()
    ax2.set_title("Rectangle under study")
    label = "$X_{max}$:"+str(box[i][0])+"   $Y_{max}$:"+str(box[i][1])+"\n$X_{min}$:"+str(box[i][3])+"   $Y_{min}$:"+str(box[i][3])
    ax2.set_xlabel(label)
    for inst in box[i][4].values():
        X = [d[1] for d in inst]
        Y = [d[2] for d in inst]
        ax2.scatter(X,Y,s=100)
    for point in box[i][5]:
        ax2.plot([point[0],point[2]],[point[1],point[3]],color='black')
    patt = "\n".join(box[i][6])
    param = "Theta: "+str(THETA)+"\nh : "+str(H/1000)+"km\nMinA : "+str(round(MINA*110*110,2))+"$km^{2}$\nMaxA : "+str(round(MAXA*110*110,2))+"$km^{2}$\nStep : "+str(STEP*110)+"km"
    ann_pattern = AnchoredText("Max Patterns :\n"+patt, loc='upper right',bbox_to_anchor=(1.24,0.8),bbox_transform=ax2.transAxes,frameon=False)
    ann_param = AnchoredText(param, loc='upper right',bbox_to_anchor=(1.3,1.03),bbox_transform=ax2.transAxes,frameon=False)
    ax2.add_artist(ann_pattern)
    ax2.add_artist(ann_param)
    return rect
