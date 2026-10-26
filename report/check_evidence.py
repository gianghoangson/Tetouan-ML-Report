"""Validate saved evidence without importing project modules or fitting models."""
from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
T = ROOT / 'results/tables'
OUT = ROOT / 'report/evidence'
checks = []
def check(name, condition):
    checks.append({'check': name, 'passed': bool(condition)})
    if not condition:
        raise AssertionError(name)

def metrics(y, p):
    e = np.asarray(p) - np.asarray(y)
    return dict(RMSE=float(np.sqrt(np.mean(e**2))), MAE=float(np.mean(abs(e))),
                MAPE=float(np.mean(abs(e / y))*100), R2=float(1-np.sum(e**2)/np.sum((y-np.mean(y))**2)))

raw = pd.read_csv(ROOT / 'data/raw/Tetuan City power consumption.csv')
raw.columns = ['DateTime','Temperature','Humidity','WindSpeed','GenDiffuse','Diffuse','Z1','Z2','Z3']
raw['DateTime'] = pd.to_datetime(raw.DateTime, format='%m/%d/%Y %H:%M')
raw = raw.set_index('DateTime').sort_index()
raw['Total'] = raw[['Z1','Z2','Z3']].sum(axis=1)
hourly = raw.resample('1h').mean()
check('Raw count 52416; hourly count 8736', len(raw)==52416 and len(hourly)==8736)
check('No missing cells, duplicate timestamps or irregular raw intervals', not raw.isna().any().any() and not raw.index.duplicated().any() and (raw.index.to_series().diff().dropna()==pd.Timedelta(minutes=10)).all())
dev = hourly.loc[hourly.index < '2017-12-01']
pred = pd.read_csv(T/'T08_test_predictions.csv',index_col=0,parse_dates=True)
final = pd.read_csv(T/'T08_final_test.csv').set_index('model')
check('720 saved predictions aligned with raw hourly December Total', len(pred)==720 and np.allclose(pred.actual,hourly.loc[pred.index,'Total']))
for model in pred.columns.drop('actual'):
    calc = metrics(pred.actual, pred[model])
    # XGBoost float32 predictions were serialized with fewer decimal places.
    check('Saved h24 prediction metrics: '+model, all(np.isclose(v,final.loc[model,k],rtol=0,atol={'RMSE':0.001,'MAE':0.001,'MAPE':0.000001,'R2':0.00000001}[k]) for k,v in calc.items()))
l1 = pd.read_csv(T/'T04_level0_level1_wide.csv').set_index('model')
l2 = pd.read_csv(T/'T05_level2_cv.csv')
l3 = pd.read_csv(T/'T07_level3_cv.csv')
h1 = pd.read_csv(T/'T10_horizon_cv.csv')
for m,g in l2.groupby('model'):
    check('Level 1 = final Level 2 fold: '+m, np.isclose(g.set_index('split').loc['fold4','RMSE'],l1.loc[m,'val_RMSE']))
s2 = pd.read_csv(T/'T05_level2_summary.csv').set_index('model')
for m,g in l2.groupby('model'):
    check('Level 2 summary: '+m, all(np.isclose(g[c].mean(),s2.loc[m,c+'_mean']) and np.isclose(g[c].std(),s2.loc[m,c+'_std']) for c in ['RMSE','MAE','MAPE','R2']))
search_report=[]
for prefix, scores, paramfile in [('',l3,'best_params.json'),('h1_',h1,'best_params_h1.json')]:
    params=json.loads((T/paramfile).read_text())
    for m,ps in params.items():
        path=T/f'search_{prefix}{m}.csv'
        df=pd.read_csv(path)
        best=df.loc[df.rank_test_RMSE.idxmin()]
        check(path.name+': chosen parameters',all((pd.isna(best['param_'+k]) if v is None else str(best['param_'+k])==str(v) or isinstance(v,(int,float)) and np.isclose(float(best['param_'+k]),v)) for k,v in ps.items()))
        g=scores[scores.model==m].set_index('split')
        check(path.name+': all selected fold metrics', all(np.isclose(g.loc[f'fold{i}',metric],float(best[f'split{i}_test_{metric}'])*factor) for i in range(5) for metric,factor in [('RMSE',-1),('MAE',-1),('MAPE',-100),('R2',1)]))
        expected={'LR':20,'DT':40,'RF':30,'SVR':30,'XGB':50}[m.split('_')[0]]
        check(path.name+': candidate count and finite scores',len(df)==expected and df.filter(regex='^mean_test_').notna().all().all())
        search_report.append({'file':path.name,'candidates':len(df),'best_row_zero_based':int(best.name),'RMSE_mean':float(-best.mean_test_RMSE),'RMSE_population_std':float(best.std_test_RMSE)})
abl=pd.read_csv(T/'T09_ablation.csv')
abls=pd.read_csv(T/'T09_ablation_summary.csv').set_index(['feature_set','model'])
for (fs,m),g in abl[abl.feature_set!='ref'].groupby(['feature_set','model']):
    check('Ablation summary '+fs+' '+m,np.isclose(g.RMSE.mean(),abls.loc[(fs,m),'RMSE_mean']) and np.isclose(g.RMSE.std(),abls.loc[(fs,m),'RMSE_std']))
check('Survey copy matches documentation',pd.read_csv(T/'T11_kaggle_survey.csv').equals(pd.read_csv(ROOT/'docs/kaggle_survey.csv')))
check('S4 reproduces absolute tuned RF test result',np.isclose(pd.read_csv(T/'T12_leakage_settings.csv').set_index('setting').loc['S4','RMSE'], final.loc['RF-tuned','RMSE']))
e=pred['SVR-tuned']-pred.actual
daily=pd.DataFrame({'MAE':e.abs().resample('D').mean(),'bias':e.resample('D').mean()})
worst=pd.read_csv(T/'T08_worst_days.csv',index_col=0,parse_dates=True)
check('Worst-day table matches saved predictions',np.allclose(daily.loc[worst.index,['MAE','bias']],worst[['MAE','bias']]))
fold0_train=hourly.loc['2017-01-08 23:00':'2017-07-03 23:00','Total']
fold0_val=hourly.loc['2017-07-04':'2017-08-02','Total']
facts={'raw_rows':len(raw),'hourly_rows':len(hourly),'first':str(raw.index.min()),'last':str(raw.index.max()),
       'h24_cv_ranking':l3.groupby('model').RMSE.mean().sort_values().to_dict(),
       'h1_cv_ranking':h1.groupby('model').RMSE.mean().sort_values().to_dict(),
       'h24_test_ranking':final.RMSE.sort_values().to_dict(),
       'dayahead_improvement_percent':100*(1-final.loc['SVR-tuned','RMSE']/final.loc['Naive-24h','RMSE']),
       'cv_horizon_improvement_percent':100*(1-h1[h1.model=='SVR'].RMSE.mean()/l3[l3.model=='SVR'].RMSE.mean()),
       'residual_bias':float(e.mean()),'residual_min':float(e.min()),'residual_max':float(e.max()),
       'december_mean_load':float(pred.actual.mean()),'fold0_train_max':float(fold0_train.max()),
       'fold0_val_max':float(fold0_val.max()),'fold0_above_train_max_percent':float((fold0_val>fold0_train.max()).mean()*100),
       'hourly_dev_correlations':dev.corr()['Total'].to_dict(),
       'monthly_total_means':hourly.Total.groupby(hourly.index.month).mean().to_dict(),
       'searches':search_report,'checks':checks}
(OUT/'numerical_checks.json').write_text(json.dumps(facts,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in facts.items() if k not in ['searches','checks','monthly_total_means','hourly_dev_correlations']},indent=2))
print(f'{len(checks)} evidence checks passed; no models trained.')
