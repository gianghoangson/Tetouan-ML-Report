"""Refresh only the slide CV diagram from saved fold boundaries; no training."""
"""Read saved evidence, verify arithmetic, and draw presentation assets. No model fitting.

Run from the report repository root: python slides/build_assets.py
Only files inside slides/ are written. The LaTeX build does not require this script.
"""
from pathlib import Path
import os
import json
import hashlib

HERE = Path(__file__).resolve().parent
REPORT = HERE.parent
WORKSPACE = REPORT.parent
ML = WORKSPACE / 'Prj Tetouan ML' / 'Machine-Learning'
TABLES = ML / 'results' / 'tables'
os.environ['MPLCONFIGDIR'] = str(HERE / '.mplconfig')
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import StrMethodFormatter
from matplotlib.patches import Patch

FIG = HERE / 'figures'
FIG.mkdir(exist_ok=True)
NAVY, BLUE, LIGHT, GREY = '#142B45', '#2767A6', '#9BB9D5', '#758491'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 15,
    'axes.labelsize': 16, 'axes.titlesize': 17, 'text.color': NAVY,
    'axes.labelcolor': NAVY, 'xtick.color': NAVY, 'ytick.color': NAVY,
    'axes.spines.top': False, 'axes.spines.right': False,
    'axes.edgecolor': '#C8D1DA', 'axes.grid': False,
    'savefig.facecolor': 'white', 'figure.facecolor': 'white', 'pdf.fonttype': 42})

def save(fig, name):
    fig.savefig(FIG / (name + '.pdf'), bbox_inches='tight', pad_inches=.08)
    fig.savefig(FIG / (name + '.png'), dpi=160, bbox_inches='tight', pad_inches=.08)
    plt.close(fig)


folds = pd.read_csv(TABLES / 'T02_cv_folds.csv')
# 1. Temporal split: exact dates, neutral description of December.
fig, ax = plt.subplots(figsize=(12.3,4.1))
start = pd.Timestamp('2017-01-08 23:00')
for i, row in folds.iterrows():
    tr_end, va_start = pd.Timestamp(row.train_end)+pd.Timedelta(hours=1), pd.Timestamp(row.val_start)
    va_end = pd.Timestamp(row.val_end)+pd.Timedelta(hours=1)
    ax.barh(i, (tr_end-start).total_seconds()/86400, left=mdates.date2num(start), color=BLUE, height=.54)
    ax.barh(i, (va_end-va_start).total_seconds()/86400, left=mdates.date2num(va_start), color=LIGHT, height=.54)
ax.axvspan(mdates.date2num(pd.Timestamp('2017-12-01')),mdates.date2num(pd.Timestamp('2017-12-31')),color='#E6EBF0')
ax.text(mdates.date2num(pd.Timestamp('2017-12-16')),2,'December\ntest',ha='center',va='center',fontsize=13)
ax.set_yticks(range(5), [f'Fold {k}' for k in range(5)])
ax.invert_yaxis()
ax.set_xlim(pd.Timestamp('2017-01-01'),pd.Timestamp('2018-01-01'))
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
ax.legend(handles=[Patch(color=BLUE,label='Expanding training window'),
                   Patch(color=LIGHT,label='Next 720 hours: validation')],
          loc='upper center',bbox_to_anchor=(.48,1.2),ncol=2,frameon=False,fontsize=16)
ax.tick_params(labelsize=18)
ax.spines['left'].set_visible(False)
ax.tick_params(axis='y',length=0)
fig.tight_layout()
save(fig,'chronological_cv')

