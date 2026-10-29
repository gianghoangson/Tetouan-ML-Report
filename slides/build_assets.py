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

checks = []
def check(name, condition):
    checks.append({'check': name, 'passed': bool(condition)})
    if not condition:
        raise AssertionError(name)

def save(fig, name):
    fig.savefig(FIG / (name + '.pdf'), bbox_inches='tight', pad_inches=.08)
    fig.savefig(FIG / (name + '.png'), dpi=160, bbox_inches='tight', pad_inches=.08)
    plt.close(fig)

def read(name):
    return pd.read_csv(TABLES / name)

cv = read('T07_default_vs_tuned.csv').set_index('model')
fold_scores = read('T07_level3_cv.csv')
test = read('T08_final_test.csv').set_index('model')
pred = pd.read_csv(TABLES / 'T08_test_predictions.csv', index_col=0, parse_dates=True)
folds = read('T02_cv_folds.csv')
hor = read('T10_horizon.csv').set_index('model')
abl = read('T09_ablation_summary.csv')
params = json.loads((TABLES / 'best_params.json').read_text())
check('December has 720 unique hourly forecasts', len(pred) == 720 and pred.index.is_unique)
check('December coverage', str(pred.index[0]) == '2017-12-01 00:00:00' and str(pred.index[-1]) == '2017-12-30 23:00:00')
actual = pred['actual']
for model in test.index:
    err = pred[model] - actual
    computed = {'RMSE': np.sqrt(np.mean(err**2)), 'MAE': np.mean(abs(err)),
        'MAPE': 100*np.mean(abs(err/actual)),
        'R2': 1-np.sum(err**2)/np.sum((actual-actual.mean())**2)}
    for metric, val in computed.items():
        # Saved XGB predictions have tiny serialization differences.
        tolerance = {'RMSE': .001, 'MAE': .001, 'MAPE': .000001, 'R2': 1e-8}[metric]
        check(f'{model}: reconstructed {metric}', abs(val-test.loc[model, metric]) < tolerance)
for model, row in cv.iterrows():
    s = fold_scores.loc[fold_scores.model == model, 'RMSE']
    check(f'{model}: CV mean and sample SD', np.allclose([s.mean(), s.std(ddof=1)], [row.tuned_RMSE_mean, row.tuned_RMSE_std]))
    search = read(f'search_{model}.csv')
    best = search.loc[search.rank_test_RMSE.idxmin()]
    check(f'{model}: selected search score', np.isclose(-best.mean_test_RMSE, s.mean()))
    check(f'{model}: five selected search folds', np.allclose([-best[f'split{k}_test_RMSE'] for k in range(5)], s.to_numpy()))
check('CV selection is absolute SVR', cv.tuned_RMSE_mean.idxmin() == 'SVR')
check('Test-best is residual SVR', test.RMSE.idxmin() == 'SVR_delta-tuned')
svr = test.loc['SVR-tuned']
gain24 = 100*(1-svr.RMSE/test.loc['Naive-24h', 'RMSE'])
gain168 = 100*(1-svr.RMSE/test.loc['Naive-168h', 'RMSE'])
gainh1 = 100*(1-hor.loc['SVR', 'h1_RMSE']/hor.loc['SVR', 'h24_RMSE'])
err = pred['SVR-tuned']-actual
daily = err.abs().groupby(pred.index.normalize()).mean()
worst = read('T08_worst_days.csv')
check('Worst day and its MAE', str(daily.idxmax().date()) == '2017-12-01' and np.isclose(daily.max(), worst.iloc[0].MAE))
raw = pd.read_csv(ML / 'data/raw/Tetuan City power consumption.csv')
check('Local raw row count', len(raw) == 52416)
raw.columns = ['DateTime', 'Temperature', 'Humidity', 'WindSpeed', 'GenDiffuse', 'Diffuse', 'Z1', 'Z2', 'Z3']
raw['DateTime'] = pd.to_datetime(raw.DateTime, format='%m/%d/%Y %H:%M')
raw = raw.set_index('DateTime')
hourly = raw.resample('1h').mean()
hourly['Total'] = hourly[['Z1','Z2','Z3']].sum(axis=1)
check('Hourly row count', len(hourly) == 8736)
check('Saved actual is hourly three-zone mean power', np.allclose(hourly.loc[pred.index, 'Total'], actual))
check('No raw missing/duplicate timestamps', not raw.isna().any().any() and raw.index.is_unique)
dev = hourly.loc[hourly.index < '2017-12-01']
season_profiles = {}
for name, months in [('Winter',[1,2]),('Spring',[3,4,5]),('Summer',[6,7,8]),('Autumn',[9,10,11])]:
    s = dev.loc[dev.index.month.isin(months)].groupby(lambda t: t.hour).Total.mean()
    season_profiles[name] = {'minimum_hour': int(s.idxmin()), 'maximum_hour': int(s.idxmax())}
check('Development profiles: minima 6-7, maxima 19-20', all(v['minimum_hour'] in [6,7] and v['maximum_hour'] in [19,20] for v in season_profiles.values()))

# Verify report figures against the specifically authorized ML repository.
figure_hashes = {}
for p in (REPORT / 'results/figures').glob('*.png'):
    q = ML / 'results/figures' / p.name
    if q.exists():
        figure_hashes[p.name] = hashlib.sha256(p.read_bytes()).hexdigest() == hashlib.sha256(q.read_bytes()).hexdigest()
for name in ['F01_total_hourly_year.png', 'F03_profile_by_season.png']:
    check(f'Reused report figure matches ML: {name}', figure_hashes[name])

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

# 2. Development ranking: all ten tuned variants, mean and sample SD.
order = cv.sort_values('tuned_RMSE_mean').index
fig, ax = plt.subplots(figsize=(8.8,5.1))
for i, model in enumerate(order):
    ax.errorbar(cv.loc[model,'tuned_RMSE_mean'],i,xerr=cv.loc[model,'tuned_RMSE_std'],fmt='o',
                color=BLUE if model=='SVR' else LIGHT,ecolor=LIGHT,capsize=3,markersize=8)
    ax.text(5600,i,f"{cv.loc[model,'tuned_RMSE_mean']:,.0f}",va='center',ha='left',fontsize=21,color=NAVY)
ax.axvline(3392.3715480968553,color=GREY,ls='--',lw=1.4)
ax.text(3420,-.9,'Naive-24h: 3,392',fontsize=16,color=GREY)
ax.set_yticks(range(len(order)),[m.replace('_delta',' Δ').replace('LR','Ridge') for m in order],fontsize=22)
ax.invert_yaxis()
ax.set_xlim(0,6500)
ax.set_xticks([0,2000,4000])
ax.set_xlabel('Development CV RMSE (kW)',fontsize=20)
ax.tick_params(axis='x',labelsize=20)
ax.xaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
ax.grid(axis='x',alpha=.18)
ax.tick_params(axis='y',length=0)
fig.tight_layout()
save(fig,'cv_ranking')

# 3. December: keep selected model first; residual SVR is explicitly observational.
models = ['SVR-tuned','Naive-24h','Naive-168h','SVR_delta-tuned']
labels = ['SVR\nCV-selected','Naive-24h','Naive-168h','SVR Δ\nobserved test-best']
fig, ax = plt.subplots(figsize=(8.7,4.5))
ax.barh(range(4),test.loc[models,'RMSE'],color=[BLUE,'#BAC5CF',GREY,LIGHT],height=.55)
for i,m in enumerate(models):
    ax.text(test.loc[m,'RMSE']+65,i,f"{test.loc[m,'RMSE']:,.1f}",va='center',fontsize=19)
ax.set_yticks(range(4),labels,fontsize=18)
ax.invert_yaxis()
ax.set_xlim(0,4050)
ax.set_xlabel('December test RMSE (kW)',fontsize=19)
ax.set_xticks([0,1000,2000,3000,4000])
ax.xaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
ax.tick_params(axis='y',length=0)
ax.grid(axis='x',alpha=.18)
ax.set_axisbelow(True)
fig.tight_layout()
save(fig,'december_comparison')

# 4. Whole December, with aligned errors: no selective week presented as the full test.
fig, (ax, er) = plt.subplots(2,1,figsize=(12.5,4.9),sharex=True,gridspec_kw={'height_ratios':[2.6,1]},layout='constrained')
ax.plot(pred.index,actual,color=NAVY,lw=1.8,label='Actual')
ax.plot(pred.index,pred['SVR-tuned'],color=BLUE,lw=1.3,ls='--',label='CV-selected SVR')
ax.set_ylabel('Mean power (kW)')
ax.yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
ax.legend(loc='upper center',bbox_to_anchor=(.5,1.2),ncol=2,frameon=False,fontsize=14)
er.plot(pred.index,err,color=BLUE,lw=1.0)
er.axhline(0,color=GREY,lw=.8)
er.set_ylabel('Error (kW)',fontsize=13)
er.set_yticks([-8000,0,8000])
er.yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
er.xaxis.set_major_locator(mdates.DayLocator(bymonthday=[1,5,10,15,20,25,30]))
er.xaxis.set_major_formatter(mdates.DateFormatter('%d Dec'))
er.set_xlim(pred.index.min(),pred.index.max())
for a in [ax,er]:
    a.axvspan(pd.Timestamp('2017-12-01'),pd.Timestamp('2017-12-02'),color=LIGHT,alpha=.3)
    a.grid(axis='y',alpha=.15)
save(fig,'december_trace')

# 5. A compact ablation keeps the exact model, target and fixed-parameter context visible.
fig, ax = plt.subplots(figsize=(10,4.3))
for model,color,mark in [('RF',BLUE,'o'),('XGB',NAVY,'s')]:
    a=abl.loc[abl.model==model].set_index('feature_set').loc[list('ABCDE')]
    ax.plot(range(5),a.RMSE_mean,color=color,marker=mark,lw=2.4,label=model+' · absolute target')
ax.axvspan(2.7,3.3,color=LIGHT,alpha=.25)
ax.set_xticks(range(5),['A\nWeather','B\n+ Calendar','C\n+ Special days','D\n+ Daily lags','E\n+ Weekly/rolling'])
ax.set_ylabel('Mean CV RMSE (kW)')
ax.yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
ax.set_ylim(0,17000)
ax.grid(axis='y',alpha=.18)
ax.legend(frameon=False,fontsize=13)
fig.tight_layout()
save(fig,'ablation')

# Numeric macros are generated from saved CSVs, reducing transcription risk.
macros={
 'TestRMSE':f'{svr.RMSE:,.1f}', 'TestMAE':f'{svr.MAE:,.1f}', 'TestMAPE':f'{svr.MAPE:.2f}',
 'TestRtwo':f'{svr.R2:.4f}', 'GainDaily':f'{gain24:.1f}', 'GainWeekly':f'{gain168:.1f}',
 'CVRMSE':f'{cv.loc["SVR","tuned_RMSE_mean"]:,.1f}', 'CVSD':f'{cv.loc["SVR","tuned_RMSE_std"]:,.1f}',
 'HoneRMSE':f'{hor.loc["SVR","h1_RMSE"]:,.1f}', 'HoneGain':f'{gainh1:.1f}',
 'DeltaTest':f'{test.loc["SVR_delta-tuned","RMSE"]:,.1f}', 'Bias':f'{err.mean():,.1f}',
 'WorstMAE':f'{daily.max():,.1f}', 'TuningGain':f'{cv.loc["SVR","improvement_%"]:.1f}',
 'RFBefore':f'{abl.query("model == \'RF\' and feature_set == \'C\'").iloc[0].RMSE_mean:,.1f}',
 'RFAfter':f'{abl.query("model == \'RF\' and feature_set == \'D\'").iloc[0].RMSE_mean:,.1f}'
}
(HERE/'metrics.tex').write_text('% Generated from saved evidence; no model fitting.\n'+''.join('\\newcommand{\\'+k+'}{'+v+'}\n' for k,v in macros.items()),encoding='utf-8')
snapshot=json.loads((HERE/'original_files_manifest.json').read_text())
for relative,digest in snapshot.items():
    check('Original unchanged: '+relative,hashlib.sha256((WORKSPACE/relative).read_bytes()).hexdigest()==digest)
result={'scope':'Saved artifacts and arithmetic only; no training or experiment execution',
    'passed':sum(x['passed'] for x in checks),'failed':sum(not x['passed'] for x in checks),
    'checks':checks,'display_values':macros,'figure_matches':figure_hashes,'profiles':season_profiles,
    'student_identity_source':'User-provided exact title-slide details',
    'paths':{'ml':str(ML),'report':str(REPORT),'output':str(HERE)}}
(HERE/'verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(f'Verified {result["passed"]} checks; failed {result["failed"]}. Five vector charts generated.')
