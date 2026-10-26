"""Typeset saved CSV/JSON evidence only. Does not train or execute notebooks."""
from pathlib import Path
import json
import math
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'report/tables'
OUT.mkdir(parents=True,exist_ok=True)
T=ROOT/'results/tables'
sources={}
def esc(s):
    return str(s).replace('&',r'\&').replace('%',r'\%').replace('_',r'\_').replace('−','-').replace('–','--').replace('…','...').replace('°C',r'$^\circ$C')
def n(x,d=1):
    if pd.isna(x): return '--'
    if round(float(x), d) == 0: x = 0.0
    return r'\num{'+f'{float(x):.{d}f}'+'}'
def name(s):
    return esc(s).replace(r'\_delta',r' $\Delta$')
def pm(a,b,d=1): return n(a,d)+r' $\pm$ '+n(b,d)
def read(f): return pd.read_csv(T/f)
def table(key,caption,heads,rows,source,cols=None,long=False):
    sources[key]={'sources':source,'caption':caption,'rows':len(rows),'columns':heads}
    cols=cols or ('l'+'r'*(len(heads)-1))
    header=' & '.join(heads)+r' \\'
    body='\n'.join(' & '.join(map(str,r))+r' \\' for r in rows)
    if long:
        text=r'\begingroup\small\setlength{\tabcolsep}{4pt}'+'\n'+r'\begin{longtable}{'+cols+'}\n'+r'\caption{'+caption+r'}\label{tab:'+key+r'}\\'+'\n'+r'\toprule'+'\n'+header+'\n'+r'\midrule\endfirsthead'+'\n'+r'\multicolumn{'+str(len(heads))+r'}{l}{\small\itshape Continued from previous page}\\\toprule'+'\n'+header+'\n'+r'\midrule\endhead\bottomrule\endfoot'+'\n'+body+'\n'+r'\end{longtable}\endgroup'+'\n'
    else:
        env='tabularx' if 'X' in cols else 'tabular'
        width=r'{\linewidth}' if env=='tabularx' else ''
        text=r'\begin{table}[tbp]\centering\small'+'\n'+r'\caption{'+caption+r'}\label{tab:'+key+'}\n'+r'\setlength{\tabcolsep}{4pt}'+'\n'+r'\begin{'+env+'}'+width+'{'+cols+'}\n'+r'\toprule'+'\n'+header+'\n'+r'\midrule'+'\n'+body+'\n'+r'\bottomrule\end{'+env+'}\n'+r'\end{table}'+'\n'
    (OUT/(key+'.tex')).write_text(text,encoding='utf-8')

d=read('T01_descriptive_stats.csv')
table('descriptive','Whole-year descriptive statistics of the original ten-minute observations (T01). Blank source units are left unspecified.',
      ['Variable','Unit','Mean','SD','Minimum','Maximum'],
      [[esc(r.iloc[0]),esc(r['unit']) if pd.notna(r['unit']) else '--',*[n(r[c],2) for c in ['mean','std','min','max']]] for _,r in d.iterrows()],['T01_descriptive_stats.csv'])
d=read('T02_split_summary.csv')
table('splits','Chronological partitions after history-related row removal (T02). All dates are in 2017; end times are 23:00.',
      ['Setting','Partition','Start','End','Hours'],
      [[r.scenario,{'Development (Train+Val)':'Development'}.get(r['set'],r['set']),r.start[5:16],r.end[5:16],n(r.rows,0)] for _,r in d.iterrows()],['T02_split_summary.csv'],cols='llrrr')
d=read('T02_cv_folds.csv')
table('folds','Expanding-window h24 cross-validation (T02). Training starts on 8 January at 23:00 in every fold; validation begins at 00:00 and ends at 23:00.',
      ['Fold','Training ends','Train hours','Validation starts','Validation ends'],
      [[n(r['fold'],0),r.train_end[:10],n(r.train_rows,0),r.val_start[:10],r.val_end[:10]] for _,r in d.iterrows()],['T02_cv_folds.csv'],cols='rlrll')
d=read('T04_level0_level1_wide.csv').sort_values('val_RMSE')
table('baselines','November validation, h24: seasonal baselines, default regressors and RF-P1 (T04). RMSE/MAE are in kW; MAPE is percent.',
      ['Model','Train RMSE','Val. RMSE','Val. MAE','MAPE','R$^2$'],
      [[name(r.model),n(r.train_RMSE),n(r.val_RMSE),n(r.val_MAE),n(r.val_MAPE,2),n(r.val_R2,4)] for _,r in d.iterrows()],['T04_level0_level1_wide.csv'])
d=read('T05_level2_summary.csv')
table('cv','Default-model development CV, h24 (T05). SD is the sample standard deviation over five folds, not a confidence interval. Errors in kW; MAPE in percent.',
      ['Model',r'RMSE mean $\pm$ SD','MAE','MAPE','R$^2$'],
      [[name(r.model),pm(r.RMSE_mean,r.RMSE_std),n(r.MAE_mean),n(r.MAPE_mean,2),n(r.R2_mean,4)] for _,r in d.iterrows()],['T05_level2_summary.csv'])
table('cv_variability',r'Supplementary default CV variability for all four metrics (T05); mean $\pm$ sample SD. RMSE/MAE in kW, MAPE in percent.',
      ['Model','RMSE','MAE','MAPE','R$^2$'],
      [[name(r.model),*[pm(r[c+'_mean'],r[c+'_std'],1 if c in ['RMSE','MAE'] else 3) for c in ['RMSE','MAE','MAPE','R2']]] for _,r in d.iterrows()],['T05_level2_summary.csv'])
d=read('T07_default_vs_tuned.csv')
table('tuning',r'Tuned h24 development CV (T07). RMSE and its SD are in kW. Improvement compares each row with the absolute default model of that family; $\Delta$ rows combine tuning with a target change.',
      ['Variant','Default RMSE',r'Tuned RMSE $\pm$ SD',r'Gain (\%)',r'MAPE (\%)'],
      [[name(r.model),n(r.default_RMSE_mean),pm(r.tuned_RMSE_mean,r.tuned_RMSE_std),n(r['improvement_%'],2),n(r.tuned_MAPE,2)] for _,r in d.iterrows()],['T07_default_vs_tuned.csv'])

d=read('T05_level2_cv.csv').pivot(index='model',columns='split',values='RMSE')
table('cv_folds','Default h24 RMSE by temporal fold (T05), in kW. Models are ordered by mean fold RMSE; fold boundaries are given in Table~\\ref{tab:folds}.',
      ['Model',*[f'Fold {k}' for k in range(5)]],
      [[name(m),*[n(d.loc[m,f'fold{k}']) for k in range(5)]] for m in d.mean(axis=1).sort_values().index],['T05_level2_cv.csv'])

rows=[]
for m,ps in json.loads((T/'best_params.json').read_text()).items():
    parts=[]
    for k,v in ps.items():
        value='None' if v is None else n(v,6) if isinstance(v,float) else esc(v)
        parts.append(esc(k.split('__')[-1])+' = '+value)
    rows.append([name(m),'; '.join(parts)])
table('selected_h24','Selected h24 hyperparameters from best\\_params.json. Estimator-wrapper prefixes are omitted; floating values are rounded to six decimals. Both target formulations were searched independently.',
      ['Variant','Selected parameters'],rows,['best_params.json'],cols=r'p{.16\linewidth}p{.76\linewidth}',long=True)
d=read('T06_search_space.csv')
rows=[]
for _,r in d.iterrows():
    p=r.hyperparameter.split('__')[-1]
    space=esc(r['search space']).replace('loguniform','log-uniform')
    rows.append([r.model,esc(p),space,n(r.n_iter,0)])
table('search_space','Search spaces shared by both horizons and both target formulations (T06). Budgets are per model formulation, not per parameter. Integer limits are inclusive as displayed.',
      ['Model','Parameter','Distribution / values','Budget'],rows,['T06_search_space.csv','src/models.py'],cols=r'p{.10\linewidth}p{.24\linewidth}p{.48\linewidth}r',long=True)
params=[]
for h,f in [('h24','best_params.json'),('h1','best_params_h1.json')]:
    for m,ps in json.loads((T/f).read_text()).items():
        for k,v in ps.items():
            value='None' if v is None else n(v,6) if isinstance(v,float) else esc(v)
            params.append([h,name(m),esc(k.split('__')[-1]),value])
table('parameters','All selected configurations from the two parameter JSON files. Wrapper prefixes are omitted; floating parameters are rounded to six decimal places here. JSON files retain full precision.',
      ['Setting','Variant','Parameter','Selected value'],params,['best_params.json','best_params_h1.json'],cols=r'lp{.20\linewidth}p{.32\linewidth}l',long=True)
d=read('T09_ablation_summary.csv').set_index(['feature_set','model'])
table('ablation','Feature ablation with fixed D-selected hyperparameters: mean CV RMSE in kW (T09). Missing entries were not run because the residual base is absent.',
      ['Set (columns)','RF','XGB',r'RF $\Delta$',r'XGB $\Delta$'],
      [[f'{fs} ({cnt})',*[n(d.loc[(fs,m),'RMSE_mean']) if (fs,m) in d.index else '--' for m in ['RF','XGB','RF_delta','XGB_delta']]] for fs,cnt in zip('ABCDEF',[5,12,15,17,21,16])],['T09_ablation_summary.csv'])
d=read('T10_horizon.csv')
table('horizon','Development CV horizon comparison (T10), RMSE in kW: best formulation within each family chosen separately per horizon. LR, DT, RF and XGB use residual targets; SVR uses the absolute target.',
      ['Model','h24 RMSE','h1 RMSE',r'h24 MAPE (\%)',r'h1 MAPE (\%)'],
      [[name(r.model),n(r.h24_RMSE),n(r.h1_RMSE),n(r.h24_MAPE,2),n(r.h1_MAPE,2)] for _,r in d.iterrows()],['T10_horizon.csv'])
for key,f,h in [('test24','T08_final_test.csv','h24'),('test1','T08_final_test_h1.csv','h1')]:
    d=read(f)
    table(key,f'December {h} evaluation (T08), ordered by observed RMSE. The CV-selected model is SVR-tuned. This ordering does not redefine selection. RMSE/MAE in kW; skill is RMSE reduction against Naive-24h.',
          ['Model','RMSE','MAE',r'MAPE (\%)','R$^2$',r'Skill (\%)'],
          [[name(r.model),n(r.RMSE),n(r.MAE),n(r.MAPE,2),n(r.R2,4),n(100*r.skill_vs_naive24,2)] for _,r in d.iterrows()],[f])
d=read('T08_worst_days.csv')
table('worst_days','Five largest daily MAEs for the selected h24 SVR (T08). Bias is prediction minus actual; all numerical columns are in kW.',
      ['Date','MAE','Bias','Actual mean','Predicted mean'],
      [[r.DateTime,n(r.MAE),n(r.bias),n(r.actual_mean),n(r.pred_mean)] for _,r in d.iterrows()],['T08_worst_days.csv'])
d=read('T12_leakage_settings.csv')
table('leakage','Four RF diagnostic settings (T12). These rows differ in task and test distribution and must not be treated as a controlled leakage-effect estimate. Errors in kW.',
      ['Setting','Train / test rows','Features','RMSE','MAE',r'MAPE (\%)','R$^2$'],
      [[r.setting,n(r.train_rows,0)+' / '+n(r.test_rows,0),n(r.features,0),n(r.RMSE),n(r.MAE),n(r.MAPE,2),n(r.R2,4)] for _,r in d.iterrows()],['T12_leakage_settings.csv'])
d=read('T12b_kfold_vs_tscv.csv')
table('kfold',r'Post-final RF search diagnostic: 20 candidates per CV strategy (T12b). Optimism is $100(\mathrm{RMSE}_{test}/\mathrm{RMSE}_{CV}-1)$. Errors in kW.',
      ['CV strategy','CV RMSE','December RMSE',r'Optimism (\%)'],
      [[esc(r.cv_method),n(r.cv_RMSE_estimate),n(r.test_RMSE),n(r['optimism_%'],2)] for _,r in d.iterrows()],['T12b_kfold_vs_tscv.csv'])
d=read('T08_final_test.csv').set_index('model')
table('runtime','Recorded h24 refit and whole-test prediction durations for selected representative models (T08). Hardware and thread configuration are not recorded in this table; timings are descriptive.',
      ['Model','Fit (s)','Predict 720 rows (s)','Test RMSE (kW)'],
      [[name(m),n(d.loc[m,'fit_time'],3),n(d.loc[m,'pred_time'],3),n(d.loc[m,'RMSE'])] for m in ['LR_delta-tuned','DT_delta-tuned','RF_delta-tuned','SVR-tuned','XGB_delta-tuned']],['T08_final_test.csv'])
facts=json.loads((ROOT/'report/evidence/numerical_checks.json').read_text())
table('search_inventory','Audit of all saved searches: number of sampled configurations and selected mean CV RMSE (kW). The row index is zero-based within the CSV data, excluding its header.',
      ['Search','Candidates','Selected row','Mean RMSE'],
      [[esc(r['file'].replace('search_','').replace('.csv','')),n(r['candidates'],0),n(r['best_row_zero_based'],0),n(r['RMSE_mean'])] for r in facts['searches']],['search_*.csv'],cols='lrrr',long=True)
rows=[]
for line in (ROOT/'requirements.txt').read_text().splitlines():
    if '==' in line:
        a,b=line.split('=='); rows.append([esc(a),b])
table('dependencies','Recorded experiment dependencies from requirements.txt; Python 3.12 is specified by the repository. These are recorded pins, not a newly reproduced environment.',
      ['Package','Pinned version'],rows,['requirements.txt'],cols='ll')
d=pd.read_csv(ROOT/'docs/kaggle_survey.csv')
rows=[]
for _,r in d.iterrows():
    owner=r.link.split('/')[3]
    rows.append([r'\href{'+r.link+'}{'+esc(owner)+'}',esc(r.target),esc(r.split),esc(r.reported_value)])
table('survey',r'Repository-authored survey of ten public GitHub projects (docs/kaggle\_survey.csv / T11). Metrics and protocol descriptions are survey transcriptions, not independently reproduced results; targets and metrics vary.',
      ['Repository owner','Target','Split / validation','Survey-reported value'],rows,['docs/kaggle_survey.csv','T11_kaggle_survey.csv'],cols=r'p{.20\linewidth}p{.22\linewidth}p{.26\linewidth}p{.23\linewidth}',long=True)
(ROOT/'report/table_sources.json').write_text(json.dumps(sources,indent=2),encoding='utf-8')
print(f'Generated {len(sources)} tables from existing evidence.')
