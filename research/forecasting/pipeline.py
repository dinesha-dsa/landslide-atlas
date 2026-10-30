"""Reproducible forecasting scaffolding. Demo output is synthetic, never field skill."""
import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import importlib.metadata
import json
from pathlib import Path
import unicodedata
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
FEATURES = ['slope_deg', 'rain_24h_mm', 'rain_72h_mm', 'rain_168h_mm']

def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, allow_nan=False)+'\n', encoding='utf-8')

def normalized(value):
    return ''.join(c for c in unicodedata.normalize('NFKD',value) if not unicodedata.combining(c)).lower()

def inventory_audit(output):
    source = ROOT/'docs/data/observations.json'
    reports = json.loads(source.read_text(encoding='utf-8'))
    mh = [r for r in reports if normalized(r.get('state',''))=='maharashtra']
    pilot = [r for r in mh if 73.02<=r['longitude']<=73.7 and 17.8<=r['latitude']<=18.6]
    summary = {'generated_utc':datetime.now(timezone.utc).isoformat(),
               'source':'NASA COOLR atlas snapshot; not an authoritative complete event inventory',
               'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
               'india_reports':len(reports),'maharashtra_reports':len(mh),
               'pilot_rectangle_reports':len(pilot),
               'maharashtra_dated_reports':sum(bool(r.get('date')) for r in mh),
               'independently_verified_forecast_labels':0,
               'missing_for_forecasting':['time-bounded verified events','mapped slope units',
                  'systematic survey coverage','reviewed non-event periods','data availability times'],
               'counts_are_reports_not_deduplicated_events':True}
    output.mkdir(parents=True,exist_ok=True)
    write_json(output/'inventory-audit.json',summary)
    columns=['id','title','date','latitude','longitude','district','location_accuracy','source_name','source_url','verification','license']
    pd.DataFrame(mh,columns=columns).to_csv(output/'maharashtra-candidate-reports.csv',index=False)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    dates=pd.to_datetime(pd.Series([r.get('date') for r in mh]),errors='coerce')
    counts=dates.dropna().dt.year.value_counts().sort_index()
    fig,ax=plt.subplots(figsize=(9,4.5),layout='constrained')
    ax.bar(counts.index,counts.values,color='#296c72')
    ax.set(title='Maharashtra: dated reports in the bundled NASA COOLR snapshot',xlabel='Reported event year',ylabel='Reports (not deduplicated events)')
    ax.spines[['top','right']].set_visible(False)
    fig.text(.01,.005,'Incomplete reporting record; no trend in hazard or forecasting skill is inferred.',fontsize=8)
    fig.savefig(output/'inventory-report-years.svg');plt.close(fig)
    return summary

def antecedent_features(issues, rainfall):
    """Only complete, nonoverlapping observed rainfall intervals available at issue time."""
    rain=rainfall.copy()
    for col in ['start_utc','end_utc','available_utc']:
        rain[col]=pd.to_datetime(rain[col],utc=True,errors='raise')
    rain['depth_mm']=pd.to_numeric(rain.depth_mm,errors='raise')
    rain['valid_fraction']=pd.to_numeric(rain.valid_fraction,errors='raise')
    if ((rain.end_utc<=rain.start_utc) | (rain.available_utc<rain.end_utc) |
        ~np.isfinite(rain.depth_mm) | (rain.depth_mm<0) |
        (rain.valid_fraction<0) | (rain.valid_fraction>1) | ~np.isfinite(rain.valid_fraction)).any():
        raise ValueError('Invalid rainfall timing, depth or cell completeness')
    rows=[]
    for issue in issues.to_dict('records'):
        time=pd.to_datetime(issue['issue_utc'],utc=True,errors='raise')
        unit=rain[(rain.unit_id==issue['unit_id']) & (rain.end_utc<=time) & (rain.available_utc<=time)]
        row=dict(issue)
        for hours in [24,72,168]:
            start=time-pd.Timedelta(hours=hours)
            selected=unit[(unit.start_utc>=start)&(unit.end_utc<=time)].sort_values('start_utc')
            complete=False
            if len(selected):
                complete=(selected.iloc[0].start_utc==start and selected.iloc[-1].end_utc==time and
                          (selected.valid_fraction==1).all() and
                          all(a==b for a,b in zip(selected.end_utc.iloc[:-1],selected.start_utc.iloc[1:])))
            row[f'rain_{hours}h_mm']=float(selected.depth_mm.sum()) if complete else None
            row[f'rain_{hours}h_complete']=bool(complete)
        rows.append(row)
    return pd.DataFrame(rows)

def validate_benchmark(frame):
    required=FEATURES+['unit_id','issue_utc','target_end_utc','outcome_available_utc','label',
                      'label_verified','coverage_verified','label_source','group_id','split']
    if set(required)-set(frame): raise ValueError('Missing columns: '+str(sorted(set(required)-set(frame))))
    data=frame.copy()
    for col in ['issue_utc','target_end_utc','outcome_available_utc']:
        data[col]=pd.to_datetime(data[col],utc=True,errors='raise')
    if data[required].isna().any().any(): raise ValueError('Missing required values')
    if not np.isfinite(data[FEATURES].to_numpy(dtype=float)).all(): raise ValueError('Features must be finite')
    if (data[FEATURES]<0).any().any(): raise ValueError('Negative terrain/rainfall values')
    if not data.label.isin([0,1]).all(): raise ValueError('Labels must be binary')
    if not data.label_verified.eq(True).all() or not data.coverage_verified.eq(True).all():
        raise ValueError('Reviewed labels and coverage are required, including for non-events')
    if data.label_source.astype(str).str.strip().eq('').any(): raise ValueError('Label provenance missing')
    if not ((data.target_end_utc-data.issue_utc)==pd.Timedelta(hours=24)).all():
        raise ValueError('This protocol requires a 24-hour target interval')
    if (data.outcome_available_utc<data.target_end_utc).any(): raise ValueError('Outcome cannot be verified before target closes')
    if data.duplicated(['unit_id','issue_utc']).any(): raise ValueError('Duplicate unit/issue')
    if set(data.split)!= {'train','validation','test'}: raise ValueError('Explicit train, validation and test partitions required')
    if data.groupby('group_id').split.nunique().gt(1).any(): raise ValueError('A related storm/event group crosses partitions')
    for split in ['train','validation','test']:
        if data[data.split==split].label.nunique()!=2: raise ValueError('Both classes needed in every partition')
    for before,after in [('train','validation'),('validation','test')]:
        if data.loc[data.split==before,'outcome_available_utc'].max()>=data.loc[data.split==after,'issue_utc'].min():
            raise ValueError('Temporal split leakage: earlier outcomes unavailable at later partition start')
    return data

def metrics(y,p,threshold):
    from sklearn.metrics import average_precision_score,brier_score_loss,roc_auc_score,confusion_matrix
    pred=p>=threshold
    tn,fp,fn,tp=confusion_matrix(y,pred,labels=[0,1]).ravel()
    return {'n':int(len(y)),'events':int(sum(y)), 'threshold':float(threshold),
            'roc_auc':float(roc_auc_score(y,p)), 'average_precision':float(average_precision_score(y,p)),
            'brier_score':float(brier_score_loss(y,p)),
            'precision':float(tp/(tp+fp)) if tp+fp else None,
            'recall':float(tp/(tp+fn)), 'false_positive_rate':float(fp/(fp+tn)),
            'tp':int(tp),'fp':int(fp),'tn':int(tn),'fn':int(fn)}

def choose_threshold(y,p):
    # Prespecified research utility: validation-only minimum (5*misses + false alarms).
    choices=np.unique(np.r_[0,p,1.000001])
    return float(min(choices,key=lambda t:(5*sum((y==1)&(p<t))+sum((y==0)&(p>=t)),-t)))

def group_confidence_intervals(y,p,groups,threshold,replicates=200):
    """Resample complete storm groups, never treat rows as independent events."""
    rng=np.random.default_rng(42); unique=np.unique(groups); values=[]
    if len(unique)<10: return {'status':'insufficient_groups','groups':int(len(unique))}
    indices={g:np.flatnonzero(groups==g) for g in unique}
    for _ in range(replicates):
        selected=np.concatenate([indices[g] for g in rng.choice(unique,len(unique),replace=True)])
        if len(np.unique(y[selected]))<2: continue
        result=metrics(y[selected],p[selected],threshold)
        values.append([result['average_precision'],result['brier_score'],result['recall'],result['false_positive_rate']])
    if len(values)<100: return {'status':'insufficient_valid_replicates'}
    bounds=np.quantile(values,[.025,.975],axis=0)
    return {'status':'computed','method':'Storm-group percentile bootstrap, fixed trained model and validation threshold; excludes training uncertainty.',
            'replicates':len(values),'groups':int(len(unique)),
            'intervals_95':{name:[float(bounds[0,i]),float(bounds[1,i])] for i,name in enumerate(['average_precision','brier_score','recall','false_positive_rate'])}}

def benchmark(frame,output,synthetic=False):
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import RandomForestClassifier,HistGradientBoostingClassifier
    from sklearn.calibration import calibration_curve
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    data=validate_benchmark(frame)
    train=data[data.split=='train']; val=data[data.split=='validation']; test=data[data.split=='test']
    models={'logistic':make_pipeline(StandardScaler(),LogisticRegression(max_iter=1000,random_state=42)),
            'random_forest':RandomForestClassifier(n_estimators=150,min_samples_leaf=8,random_state=42,n_jobs=1),
            'hist_gradient_boosting':HistGradientBoostingClassifier(max_iter=100,max_leaf_nodes=7,l2_regularization=2,random_state=42)}
    output.mkdir(parents=True,exist_ok=True)
    results={};predictions=test[['unit_id','issue_utc','label','group_id']].copy()
    fig,ax=plt.subplots(figsize=(6,5),layout='constrained');ax.plot([0,1],[0,1],':',color='gray')
    # A simple rainfall-only logistic baseline is train-fitted; no guessed operational threshold.
    models['rainfall_only']=make_pipeline(StandardScaler(),LogisticRegression(max_iter=1000,random_state=42))
    models['terrain_only']=make_pipeline(StandardScaler(),LogisticRegression(max_iter=1000,random_state=42))
    for name,model in models.items():
        columns=['slope_deg'] if name=='terrain_only' else (['rain_24h_mm','rain_72h_mm','rain_168h_mm'] if name=='rainfall_only' else FEATURES)
        model.fit(train[columns],train.label)
        pv=model.predict_proba(val[columns])[:,1]
        threshold=choose_threshold(val.label.to_numpy(),pv)
        pt=model.predict_proba(test[columns])[:,1]
        results[name]=metrics(test.label.to_numpy(),pt,threshold)
        results[name]['uncertainty']=group_confidence_intervals(test.label.to_numpy(),pt,test.group_id.to_numpy(),threshold)
        predictions[name]=pt
        observed,forecast=calibration_curve(test.label,pt,n_bins=5,strategy='quantile')
        ax.plot(forecast,observed,'o-',label=name.replace('_',' '))
    constant=np.full(len(test),train.label.mean())
    results['training_prevalence']=metrics(test.label.to_numpy(),constant,.5)
    ax.set(xlabel='Mean predicted probability',ylabel='Observed event fraction',
           title=('SYNTHETIC SOFTWARE DEMO' if synthetic else 'Research test set')+'\nReliability diagram',xlim=(0,1),ylim=(0,1))
    ax.legend(fontsize=8);fig.savefig(output/'reliability.svg');plt.close(fig)
    predictions.to_csv(output/'test-predictions.csv',index=False)
    report={'synthetic':synthetic,'forecasting_skill_validated':False,
            'interpretation':'Synthetic software check; no Maharashtra performance claim.' if synthetic else 'Retrospective research result; requires independent review and prospective validation.',
            'features':FEATURES,'threshold_policy':'Validation-only minimum 5*FN + FP; illustrative research utility, not an approved operational warning policy.',
            'seed':42,'partitions':data.split.value_counts().to_dict(),'models':results,
            'input_table_sha256':hashlib.sha256(frame.to_csv(index=False).encode()).hexdigest(),
            'environment':{name:importlib.metadata.version(name) for name in ['numpy','pandas','scikit-learn','matplotlib']},
            'limitations':['No prospective validation','Bootstrap excludes model-fitting and inventory uncertainty',
                          'No spatial-transfer evaluation in this temporal benchmark','No latency-aware weather-forecast predictors ingested']}
    write_json(output/'metrics.json',report)
    return report

def synthetic_data():
    rng=np.random.default_rng(42); rows=[]
    for year,split in [(2021,'train'),(2022,'validation'),(2023,'test')]:
        for day in range(100):
            issue=datetime(year,6,1,tzinfo=timezone.utc)+timedelta(days=day)
            storm=rng.gamma(2,12)
            for unit in range(5):
                slope=10+unit*8; rain=max(0,storm+rng.normal(0,4))
                chance=1/(1+np.exp(-(-5+.055*slope+.045*rain)))
                rows.append({'unit_id':f'SYNTHETIC-{unit}','issue_utc':issue.isoformat(),
                             'target_end_utc':(issue+timedelta(hours=24)).isoformat(),
                             'outcome_available_utc':(issue+timedelta(hours=72)).isoformat(),
                             'slope_deg':slope,'rain_24h_mm':rain,'rain_72h_mm':rain+rng.gamma(2,15),
                             'rain_168h_mm':rain+120+rng.gamma(2,20),'label':int(rng.random()<chance),
                             'label_verified':True,'coverage_verified':True,'label_source':'SYNTHETIC SOFTWARE FIXTURE',
                             'group_id':f'SYNTHETIC-{year}-{day//5}','split':split})
    return pd.DataFrame(rows)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    a=sub.add_parser('audit');a.add_argument('--output',type=Path,default=HERE/'outputs/inventory')
    d=sub.add_parser('demo');d.add_argument('--output',type=Path,default=HERE/'outputs/synthetic-demo')
    f=sub.add_parser('features');f.add_argument('--issues',type=Path,required=True);f.add_argument('--rainfall',type=Path,required=True);f.add_argument('--output',type=Path,required=True)
    b=sub.add_parser('benchmark');b.add_argument('--input',type=Path,required=True);b.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.command=='audit': print(json.dumps(inventory_audit(args.output)))
    elif args.command=='demo':
        args.output.mkdir(parents=True,exist_ok=True)
        data=synthetic_data();data.to_csv(args.output/'synthetic-input.csv',index=False)
        benchmark(data,args.output,synthetic=True);print('Synthetic software demonstration completed; no field forecasting claim.')
    elif args.command=='features':
        out=antecedent_features(pd.read_csv(args.issues),pd.read_csv(args.rainfall))
        args.output.parent.mkdir(parents=True,exist_ok=True);out.to_csv(args.output,index=False)
    else: benchmark(pd.read_csv(args.input),args.output)

if __name__=='__main__': main()
