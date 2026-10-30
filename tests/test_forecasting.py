import importlib.util
from pathlib import Path
import unittest
import pandas as pd

spec=importlib.util.spec_from_file_location('forecast',Path(__file__).resolve().parents[1]/'research/forecasting/pipeline.py')
forecast=importlib.util.module_from_spec(spec);spec.loader.exec_module(forecast)

class ForecastTests(unittest.TestCase):
    def rain(self):
        times=pd.date_range('2026-06-01',periods=169,freq='h',tz='UTC')
        return pd.DataFrame({'unit_id':['A']*168,'start_utc':times[:-1],'end_utc':times[1:],
                             'available_utc':times[1:],'depth_mm':[1.]*168,'valid_fraction':[1.]*168})
    def issues(self):
        return pd.DataFrame([{'unit_id':'A','issue_utc':'2026-06-08T00:00:00Z','slope_deg':30}])
    def test_complete_interval_integrates_depth(self):
        x=forecast.antecedent_features(self.issues(),self.rain()).iloc[0]
        self.assertEqual(x.rain_24h_mm,24);self.assertEqual(x.rain_168h_mm,168)
    def test_late_rain_is_not_available(self):
        rain=self.rain();rain.loc[167,'available_utc']=pd.Timestamp('2026-06-08T04:00:00Z')
        x=forecast.antecedent_features(self.issues(),rain).iloc[0]
        self.assertIsNone(x.rain_24h_mm)
    def test_gap_overlap_and_partial_coverage_are_missing(self):
        for mode in ['gap','overlap','partial']:
            rain=self.rain()
            if mode=='gap':rain=rain.drop(index=160)
            elif mode=='overlap':rain=pd.concat([rain,rain.iloc[[160]]],ignore_index=True)
            else:rain.loc[160,'valid_fraction']=.9
            self.assertIsNone(forecast.antecedent_features(self.issues(),rain).iloc[0].rain_24h_mm)
    def test_negative_rain_rejected(self):
        rain=self.rain();rain.loc[0,'depth_mm']=-1
        with self.assertRaises(ValueError): forecast.antecedent_features(self.issues(),rain)
    def test_valid_chronological_demo(self):
        self.assertEqual(len(forecast.validate_benchmark(forecast.synthetic_data())),1500)
    def test_shared_storm_and_unverified_negatives_rejected(self):
        for mode in ['storm','coverage','label']:
            data=forecast.synthetic_data()
            if mode=='storm':data.loc[500,'group_id']=data.loc[0,'group_id']
            elif mode=='coverage':data.loc[0,'coverage_verified']=False
            else:data.loc[0,'label_verified']=False
            with self.assertRaises(ValueError):forecast.validate_benchmark(data)
    def test_late_training_outcome_rejected(self):
        data=forecast.synthetic_data();data.loc[0,'outcome_available_utc']='2024-01-01T00:00:00Z'
        with self.assertRaises(ValueError):forecast.validate_benchmark(data)
    def test_threshold_is_chosen_without_test_labels(self):
        import numpy as np
        threshold=forecast.choose_threshold(np.array([0,1,0,1]),np.array([.1,.6,.3,.9]))
        self.assertAlmostEqual(threshold,.6)
    def test_duplicate_unit_issue_rejected(self):
        data=forecast.synthetic_data();data=pd.concat([data,data.iloc[[0]]])
        with self.assertRaises(ValueError):forecast.validate_benchmark(data)

if __name__=='__main__': unittest.main()
