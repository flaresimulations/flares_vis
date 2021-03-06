import sys

import matplotlib as mpl
mpl.use('Agg')  # for SLURM use
import matplotlib.pyplot as plt
import numpy as np
import eagle as E

import sphviewer as sph
from sphviewer.tools import cmaps as sph_cmaps  # custom py-sphviewer cmaps
import vis_util
# from importlib import reload  
# reload(vis_util)

sim = '/cosma7/data/dp004/dc-love2/data/G-EAGLE/geagle_0000/data' 
tag = '014_z004p770'

## get input
if len(sys.argv) > 1:
    n1 = int(sys.argv[1])
    n2 = int(sys.argv[2])
    nrange = np.arange(n1,n2)
else:
    nrange = np.arange(0,360)

## particle properties

coods = E.readArray("SNAPSHOT", sim, tag, "/PartType4/Coordinates", numThreads=1)
pmass = E.readArray("SNAPSHOT", sim, tag, "/PartType4/Mass", numThreads=1)
phsml = E.readArray("SNAPSHOT", sim, tag, "/PartType4/SmoothingLength", numThreads=1)

## subhalo properties

sh_cop = E.readArray("SUBFIND", sim, tag, "/Subhalo/CentreOfPotential", numThreads=1)
sh_mstar = E.readArray("SUBFIND", sim, tag, "/Subhalo/Stars/Mass", numThreads=1)
spin = E.readArray("SUBFIND", sim, tag, "/Subhalo/GasSpin", numThreads=1)

## set centre of box

idx = np.argsort(sh_mstar)[::-1][1]
a,b,c = sh_cop[idx]      # use most massive (mstar) halo

## Align with spin axis of galaxy

s = spin[idx]
t = np.arctan(s[0]/s[2])# * 90./np.pi
#p = np.arctan(s[1]/s[2]) * 30./np.pi

## Create particle and camera objects

P = sph.Particles(np.array(coods - [a,b,c]), 
                  pmass / pmass.min())#, hsml = phsml)

C = sph.Camera(x=0,y=0,z=0,
               r=.03,zoom=7,
               t=t,p=p,roll=0,
               xsize=4000,ysize=2250)  # 16:9


S = sph.Scene(P, Camera=C)

## loop round object
for i in nrange:

    print("p = %s"%i)
    sys.stdout.flush()

    ## update scene camera
    S.update_camera(p=i)

    R = sph.Render(S)
    
    ## Get image and plot
    R.set_logscale()
    img = R.get_image()
    # img = sph_cmaps.desert()(vis_util.get_normalized_image(img,vmin=0.4,vmax=3.2))
    img = plt.get_cmap('gray')(vis_util.get_normalized_image(img,vmin=None,vmax=.25))

    fig, ax = vis_util.plot_img(img, R.get_extent())

    fig.savefig('movie_images/stars_test_zoom_p03_r_%03d.png'% i, bbox_inches='tight', pad_inches=0)

    plt.close()


