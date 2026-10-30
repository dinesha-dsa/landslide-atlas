import importlib.util
from datetime import datetime, timezone
from pathlib import Path
import tempfile
import unittest
import h5py
import numpy as np

spec = importlib.util.spec_from_file_location('feeds', Path(__file__).resolve().parents[1]/'scripts/refresh_satellite_feeds.py')
feeds = importlib.util.module_from_spec(spec)
spec.loader.exec_module(feeds)

class SatelliteTests(unittest.TestCase):
    def test_interval_and_midnight(self):
        a,b = feeds.granule_interval('3B-HHR-E.X.20261029-S233000-E235959.1410.V07C.HDF5')
        self.assertEqual((b-a).total_seconds(),1800)
        self.assertEqual(b.day,30)

    def test_missing_cells_not_zero_and_units(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary)/'3B-HHR-E.X.20261029-S120000-E122959.0720.V07C.HDF5'
            with h5py.File(path,'w') as f:
                g=f.create_group('Grid')
                g['lon']=[73.1,73.2]; g['lat']=[18.1,18.2]
                d=g.create_dataset('precipitation',data=np.array([[[2.,-9999.9],[2.,2.]]],dtype='f4'))
                d.attrs['units']='mm/hr'; d.attrs['_FillValue']=np.float32(-9999.9)
            now=datetime(2026,10,30,tzinfo=timezone.utc)
            result=feeds.summarize_imerg(path,now)
            self.assertEqual(result['valid_cells'],3)
            self.assertAlmostEqual(result['mean_rate_mm_hr'],2)
            self.assertAlmostEqual(result['mean_depth_mm_30min'],1)
            with h5py.File(path,'a') as f:
                f['Grid/precipitation'].attrs['units']='unknown'
            with self.assertRaises(ValueError): feeds.summarize_imerg(path,now)

    def test_future_granule_rejected(self):
        path=Path('3B-HHR-E.X.20991029-S120000-E122959.0720.V07C.HDF5')
        with self.assertRaises(ValueError):
            feeds.summarize_imerg(path,datetime.now(timezone.utc))

    def test_no_valid_pixels_is_missing(self):
        with tempfile.TemporaryDirectory() as temporary:
            path=Path(temporary)/'3B-HHR-E.X.20261029-S120000-E122959.0720.V07C.HDF5'
            with h5py.File(path,'w') as f:
                g=f.create_group('Grid');g['lon']=[73.1];g['lat']=[18.1]
                d=g.create_dataset('precipitation',data=[[[-9999.9]]]);d.attrs['units']='mm/hr'
            r=feeds.summarize_imerg(path,datetime(2026,10,30,tzinfo=timezone.utc))
            self.assertIsNone(r['mean_rate_mm_hr']);self.assertIsNone(r['mean_depth_mm_30min'])

if __name__=='__main__': unittest.main()
