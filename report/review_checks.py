"""Targeted peer-review checks; reads project artifacts and never fits models."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[1]
T = ROOT / 'results/tables'
checks = []
def check(name, ok):
    checks.append({'check': name, 'passed': bool(ok)})

raw = pd.read_csv(ROOT / 'data/raw/Tetuan City power consumption.csv')
raw.columns = ['DateTime','Temperature','Humidity','WindSpeed','GenDiffuse','Diffuse','Z1','Z2','Z3']
raw['DateTime'] = pd.to_datetime(raw.DateTime, format='%m/%d/%Y %H:%M')
raw = raw.set_index('DateTime').sort_index()
raw['Total'] = raw[['Z1','Z2','Z3']].sum(axis=1)
hourly = raw.resample('1h').mean()
dev = hourly.loc[hourly.index < '2017-12-01']
checks_expected = {7:88174, 11:65105, 12:63751}
for month, expected in checks_expected.items():
    check(f'EDA month {month} mean rounds to narrative',
          round(hourly.loc[hourly.index.month == month, 'Total'].mean()) == expected)
check('Raw total mean rounds to 71222.9 kW', round(raw.Total.mean(), 1) == 71222.9)
check('Wind proportions match narrative', round(100*(raw.WindSpeed <= .1).mean(), 1) == 57.0
      and round(100*((raw.WindSpeed > 4.8) & (raw.WindSpeed <= 5.1)).mean(), 1) == 38.6)
wk = dev.groupby(dev.index.dayofweek).Total.mean()
check('Sunday mean difference rounds to -5.9 percent', round(100*(wk[6]/wk.loc[0:4].mean()-1),1) == -5.9)
centered = dev.Total.to_numpy() - dev.Total.mean()
acf = {lag:float(np.dot(centered[lag:], centered[:-lag])/np.dot(centered,centered)) for lag in [24,168]}
check('Development ACF agrees at reported precision', round(acf[24],2)==.98 and round(acf[168],2)==.95)

# Reproduce only the row split from notebook 08, not its RF fits.
data10 = raw.assign(lag_10min=raw.Total.shift(1)).dropna()
train, test = train_test_split(np.arange(len(data10)), test_size=.25, shuffle=True, random_state=42)
train_mask = np.zeros(len(data10), dtype=bool)
train_mask[train] = True
test_mask = ~train_mask
leaked_predecessors = np.flatnonzero(train_mask[1:] & test_mask[:-1])
count = len(leaked_predecessors)
check('S2 split counts reproduce saved T12', len(train)==39311 and len(test)==13104)
check('S2 contains held-out targets in successor training-row lag inputs', count > 0)
check('S2 count in the reviewed report is 9834 of 13104', count == 9834 and len(test) == 13104)
check('Identified successor features equal their held-out predecessor targets', np.array_equal(
    data10.lag_10min.iloc[leaked_predecessors+1].to_numpy(),
    data10.Total.iloc[leaked_predecessors].to_numpy()))
cv = pd.read_csv(T / 'T07_level3_cv.csv').groupby('model')[['RMSE','MAE','MAPE']].mean()
pred = pd.read_csv(T / 'T08_test_predictions.csv',index_col=0,parse_dates=True)
group_errors={}
for weekday in [0,2]:
    part=pred.loc[pred.index.dayofweek == weekday]
    group_errors[weekday]={m:float((part[m]-part.actual).abs().mean()) for m in ['SVR-tuned','Naive-24h']}
check('Monday selected/naive MAEs round to 1007/5294',
      [round(x) for x in group_errors[0].values()] == [1007,5294])
check('Wednesday selected/naive MAEs round to 710/562',
      [round(x) for x in group_errors[2].values()] == [710,562])
best_metrics={metric:cv[metric].idxmin() for metric in cv}
check('Tuned CV RMSE/MAE/MAPE winners match audit', best_metrics ==
      {'RMSE':'SVR','MAE':'RF_delta','MAPE':'RF_delta'})
result={'checks':checks,'passed':sum(c['passed'] for c in checks),
        'failed':sum(not c['passed'] for c in checks),
        'S2_test_targets_in_training_lags':count,
        'S2_fraction_of_test_targets_in_training_lags':count/len(test),
        'h24_tuned_cv_metric_winners':best_metrics,
        'development_acf':acf,'weekday_mae':group_errors,
        'note':'Index-only split and saved-data calculations; no training or performance re-estimation.'}
(ROOT/'report/evidence/peer_review_checks.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
if result['failed']:
    raise SystemExit(1)
