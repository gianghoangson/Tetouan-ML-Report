"""Typeset saved CSV/JSON evidence only. Does not train or execute notebooks."""
from pathlib import Path
import json
import math
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'report/tables'
OUT.mkdir(parents=True,exist_ok=True)
# Project repository holding results/tables, docs/ and requirements.txt (this report repo sits inside it)
REPO=ROOT if (ROOT/'results/tables').exists() else ROOT.parent
T=REPO/'results/tables'
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
        text=r'\begin{table}[H]\centering\small'+'\n'+r'\caption{'+caption+r'}\label{tab:'+key+'}\n'+r'\setlength{\tabcolsep}{4pt}'+'\n'+r'\begin{'+env+'}'+width+'{'+cols+'}\n'+r'\toprule'+'\n'+header+'\n'+r'\midrule'+'\n'+body+'\n'+r'\bottomrule\end{'+env+'}\n'+r'\end{table}'+'\n'
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
table('baselines','Level 0 and Level 1: November validation of the seasonal baselines and the default regressors, h24 (T04). RMSE/MAE in kW; MAPE in percent.',
      ['Model','Train RMSE','Val. RMSE','Val. MAE','MAPE','R$^2$'],
      [[name(r.model),n(r.train_RMSE),n(r.val_RMSE),n(r.val_MAE),n(r.val_MAPE,2),n(r.val_R2,4)] for _,r in d.iterrows()],['T04_level0_level1_wide.csv'])
d=read('T05_level2_summary.csv')
table('cv','Default-model development CV, h24 (T05). SD is the sample standard deviation over five folds, not a confidence interval. Errors in kW; MAPE in percent.',
      ['Model',r'RMSE mean $\pm$ SD','MAE','MAPE','R$^2$'],
      [[name(r.model),pm(r.RMSE_mean,r.RMSE_std),n(r.MAE_mean),n(r.MAPE_mean,2),n(r.R2_mean,4)] for _,r in d.iterrows()],['T05_level2_summary.csv'])
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
rows=[]; prev=None
for _,r in d.iterrows():
    first = r.model != prev
    space=esc(r['search space']).replace('loguniform','log-uniform').replace('randint','integer').replace('uniform(','uniform(')
    rows.append(((r'\addlinespace ' if first and prev is not None else '')+(r.model if first else ''), n(r.n_iter,0) if first else '', r'\code{'+r.hyperparameter.split('__')[-1]+'}', space))
    prev=r.model
table('search_space','Hyperparameter search spaces (T06). Each model is tuned twice (absolute and relative target) with the same space; \\emph{Candidates} is the number of sampled configurations.',
      ['Model','Candidates','Hyperparameter','Values / distribution'],rows,['T06_search_space.csv','notebooks/02_models.ipynb (Part 5)'],cols='lrll')
d=read('T09_ablation_summary.csv').set_index(['feature_set','model'])
table('ablation','Feature ablation with fixed D-selected hyperparameters: mean CV RMSE in kW (T09). Missing entries were not run because the residual base is absent.',
      ['Set (columns)','RF','XGB',r'RF $\Delta$',r'XGB $\Delta$'],
      [[f'{fs} ({cnt})',*[n(d.loc[(fs,m),'RMSE_mean']) if (fs,m) in d.index else '--' for m in ['RF','XGB','RF_delta','XGB_delta']]] for fs,cnt in zip('ABCDEF',[5,12,15,17,21,16])],['T09_ablation_summary.csv'])
d=read('T10_horizon.csv')
table('horizon','Horizon comparison on development CV (T10): mean RMSE in kW and MAPE in percent. Each model keeps its h24 target type and hyperparameters at both horizons.',
      ['Model','Target','h24 RMSE','h1 RMSE',r'h24 MAPE (\%)',r'h1 MAPE (\%)'],
      [[name(r.model),'--' if pd.isna(r.version) else ('relative' if r.version.startswith('relative') else 'absolute'),n(r.h24_RMSE),n(r.h1_RMSE),n(r.h24_MAPE,2),n(r.h1_MAPE,2)] for _,r in d.iterrows()],['T10_horizon.csv'],cols='llrrrr')
for key,f,h in [('test24','T08_final_test.csv','h24')]:
    d=read(f)
    table(key,f'December test, {h} (T08), ordered by test RMSE. The model chosen on CV before the test is SVR-tuned. RMSE/MAE in kW; skill is the RMSE reduction against Naive-24h.',
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
table('kfold',r'Tuning the same RF with shuffled KFold or TimeSeriesSplit, 20 candidates each (T12b). Optimism $=100(\mathrm{RMSE}_{test}/\mathrm{RMSE}_{CV}-1)$; errors in kW.',
      ['CV strategy','CV RMSE','December RMSE',r'Optimism (\%)'],
      [[esc(r.cv_method),n(r.cv_RMSE_estimate),n(r.test_RMSE),n(r['optimism_%'],2)] for _,r in d.iterrows()],['T12b_kfold_vs_tscv.csv'])
d=read('T08_final_test.csv').set_index('model')
table('runtime','Refit and prediction time of the tuned h24 models (T08), single run; timings are indicative.',
      ['Model','Fit (s)','Predict 720 rows (s)','Test RMSE (kW)'],
      [[name(m),n(d.loc[m,'fit_time'],3),n(d.loc[m,'pred_time'],3),n(d.loc[m,'RMSE'])] for m in ['LR_delta-tuned','DT_delta-tuned','RF_delta-tuned','SVR-tuned','XGB_delta-tuned']],['T08_final_test.csv'])
rows=[]
for line in (REPO/'requirements.txt').read_text().splitlines():
    if '==' in line:
        a,b=line.split('=='); rows.append([esc(a),b])
table('dependencies','Recorded experiment dependencies from requirements.txt; Python 3.12 is specified by the repository. These are recorded pins, not a newly reproduced environment.',
      ['Package','Pinned version'],rows,['requirements.txt'],cols='ll')
d=pd.read_csv(REPO/'docs/kaggle_survey.csv')
# Short labels for the compact survey table (the full text stays in docs/kaggle_survey.csv)
TARGET={'Total (also each zone)':'Total','Zone 1, 2, 3 (separate models)':'Each zone','Zone 1, 2, 3 (per-zone models)':'Each zone',
        'Mean of 3 zones (min-max scaled)':'Mean of zones'}
RESULT={'Kevinbui16':'RMSE 2,624 kW','niharkaria':'R$^2$ 0.986','nayana142':'R$^2$ 0.956$^a$','Merci93':'R$^2$ 0.82--0.91',
        'SoukainaBoufousse':'RMSE 353 kW (Zone 3)','ThiagoLevis':'R$^2$ 0.19--0.29','ruwindarowel':'RMSE 9,907 kW',
        'atishk28':'R$^2$ 0.834','daniahfarooq':'R$^2$ 0.973 (Zone 1)','AtharvaPandey-coder':'R$^2$ 0.971'}
def split_short(r):
    import re
    m=re.search(r'(\d+)/(\d+)',r.split)
    if 'KFold' in r.split: return 'random (K-fold)'
    return ('chronological ' if r.shuffled=='no' else 'random ')+(m.group(0) if m else '')
rows=[]
for _,r in d.iterrows():
    owner=r.link.split('/')[3]
    lags='no' if r.uses_lag=='no' else ('1 h, 24 h' if '1 h' in r.uses_lag else 'last 24 h')
    rows.append([r'\href{'+r.link+'}{'+esc(owner)+'}',TARGET.get(r.target,esc(r.target)),r.resolution,split_short(r),lags,RESULT[owner]])
sources['survey']={'sources':['docs/kaggle_survey.csv','T11_kaggle_survey.csv'],'rows':len(rows)}
text=(r'\begin{table}[H]\centering\small'+'\n'
      r'\caption{Survey of ten public GitHub projects on the Tetouan dataset (T11), read from their code. Results are as reported by each project and use different targets and splits.}\label{tab:survey}'+'\n'
      r'\setlength{\tabcolsep}{4pt}'+'\n'
      r'\begin{tabular}{@{}llllll@{}}'+'\n'r'\toprule'+'\n'
      r'Repository & Target & Data & Split & Load lags & Reported result \\'+'\n'r'\midrule'+'\n'
      + '\n'.join(' & '.join(x)+r' \\' for x in rows)+'\n'
      r'\bottomrule\end{tabular}'+'\n'
      r'\par\smallskip{\footnotesize $^a$ Uses the other zones at the same timestamp as inputs (leakage).}'+'\n'
      r'\end{table}'+'\n')
(OUT/'survey.tex').write_text(text,encoding='utf-8')
(ROOT/'report/table_sources.json').write_text(json.dumps(sources,indent=2),encoding='utf-8')
print(f'Generated {len(sources)} tables from existing evidence.')
