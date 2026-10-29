"""Draw the existing F04 right-panel data with larger slide labels; no model fitting."""
from pathlib import Path
import os
HERE=Path(__file__).resolve().parent
os.environ['MPLCONFIGDIR']=str(HERE/'.mplconfig')
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
raw=HERE.parent.parent/'Prj Tetouan ML'/'Machine-Learning'/'data/raw/Tetuan City power consumption.csv'
d=pd.read_csv(raw)
d.columns=['dt','Temperature','Humidity','WindSpeed','GenDiffuse','Diffuse','Z1','Z2','Z3']
d['dt']=pd.to_datetime(d.dt,format='%m/%d/%Y %H:%M')
y=d.set_index('dt')[['Z1','Z2','Z3']].sum(axis=1).resample('1h').mean()
dev=y.loc[y.index<'2017-12-01']
hw=dev.groupby([dev.index.hour,dev.index.dayofweek]).mean().unstack()
rel=(hw.div(hw[[0,1,2,3,4]].mean(axis=1),axis=0)-1)*100
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':15,'text.color':'#142B45',
 'axes.labelcolor':'#142B45','xtick.color':'#142B45','ytick.color':'#142B45','pdf.fonttype':42})
fig,ax=plt.subplots(figsize=(5.8,4.9),layout='constrained')
lim=np.ceil(rel.abs().max().max())
mesh=ax.pcolormesh(np.arange(8),np.arange(25),rel.values,cmap='RdBu_r',
 vmin=-lim,vmax=lim,edgecolors='white',linewidth=.5)
ax.set_xticks(np.arange(7)+.5,['M','Tu','W','Th','F','Sa','Su'])
ax.set_yticks(np.arange(0,24,4)+.5,range(0,24,4))
ax.invert_yaxis()
ax.set_ylabel('Hour of day')
ax.tick_params(length=0)
for spine in ax.spines.values(): spine.set_visible(False)
cb=fig.colorbar(mesh,ax=ax,pad=.03,shrink=.9)
cb.set_ticks([-15,0,15], labels=['-15%','0%','+15%'])
cb.outline.set_visible(False)
ax.set_title('Difference from weekdays',fontsize=16)
fig.savefig(HERE/'figures/weekday_difference.pdf',bbox_inches='tight',pad_inches=.05)
plt.close(fig)
wk=dev.groupby(dev.index.dayofweek).mean()
print('Sunday mean difference:',100*(wk[6]/wk.loc[0:4].mean()-1))
print('Sunday 7-8h:',rel.loc[[7,8],6].tolist())


# F07 projection view: same biased ACF estimator, fewer ticks and larger labels.
z=dev.to_numpy()-dev.mean()
n=2*len(z)
corr=np.fft.irfft(np.abs(np.fft.rfft(z,n=n))**2,n=n)[:201]
corr=corr/corr[0]
fig,ax=plt.subplots(figsize=(8,2.65),layout='constrained')
ax.vlines(np.arange(1,201),0,corr[1:],color='#2767A6',lw=.7)
ax.axhline(0,color='#526679',lw=.8)
for lag in [24,48,168]:
 ax.plot(lag,corr[lag],'o',color='#142B45',ms=4)
 ax.axvline(lag,color='#526679',ls='--',lw=.6,alpha=.5)
ax.set_xlim(0,201)
ax.set_ylim(-.3,1.1)
ax.set_xticks([0,24,48,96,168,200])
ax.set_yticks([0,.5,1])
ax.set_xlabel('Lag (hours)',fontsize=15)
ax.set_ylabel('ACF',fontsize=15)
ax.grid(axis='y',alpha=.15)
for spine in ['top','right']: ax.spines[spine].set_visible(False)
fig.savefig(HERE/'figures/acf_view.pdf',bbox_inches='tight',pad_inches=.05)
plt.close(fig)
print('Saved ACF at 24/48/168:',corr[[24,48,168]].tolist())
