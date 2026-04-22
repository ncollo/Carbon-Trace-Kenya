"""
Enhanced data ingestion pipeline for Carbon Trace Kenya datasets.
Handles loading, validation, and storage of all dataset types.
"""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dataset_dir = Path("dataset_csv")


@dataclass
class DatasetConfig:
    """Configuration for a dataset type"""
    name: str
    path_pattern: str  # e.g., "fuel_card_*.csv"
    key_id_col: str  # Primary identifier column
    required_cols: List[str]
    numeric_cols: List[str]
    categorical_cols: List[str]


# Dataset configurations
DATASET_CONFIGS = {
    'fuel_card': DatasetConfig(
        name='Fuel Card Records',
        path_pattern='fuel_card_*.csv',
        key_id_col='record_id',
        required_cols=['company_name', 'nse_code', 'vehicle_id', 'fuel_litres', 'emission_tco2e'],
        numeric_cols=['fuel_litres', 'fuel_cost_ksh', 'gps_km_driven', 'emission_kgco2e', 'emission_tco2e'],
        categorical_cols=['vehicle_class', 'fuel_type', 'fuel_station_brand', 'sector']
    ),
    'anomaly': DatasetConfig(
        name='Anomaly Detection',
        path_pattern='anomaly_*.csv',
        key_id_col='anomaly_record_id',
        required_cols=['company_name', 'vehicle_id', 'fuel_pattern_flag'],
        numeric_cols=['fuel_litres_expected', 'fuel_litres_actual', 'anomaly_score'],
        categorical_cols=['vehicle_class', 'anomaly_type', 'sector']
    ),
    'commute': DatasetConfig(
        name='Employee Commute',
        path_pattern='commute_*.csv',
        key_id_col='commute_record_id',
        required_cols=['company_name', 'employee_id', 'transport_mode', 'distance_km'],
        numeric_cols=['distance_km', 'emission_kgco2e'],
        categorical_cols=['transport_mode', 'vehicle_type', 'sector']
    ),
    'travel': DatasetConfig(
        name='Business Travel',
        path_pattern='travel_*.csv',
        key_id_col='travel_record_id',
        required_cols=['company_name', 'trip_type', 'distance_km'],
        numeric_cols=['distance_km', 'emission_kgco2e', 'journey_count'],
        categorical_cols=['trip_type', 'transport_method', 'sector']
    ),
    'gps_log': DatasetConfig(
        name='GPS Tracking',
        path_pattern='gps_log_*.csv',
        key_id_col='gps_record_id',
        required_cols=['fuel_record_id', 'vehicle_id', 'latitude', 'longitude'],
        numeric_cols=['latitude', 'longitude', 'altitude', 'distance_segment_km'],
        categorical_cols=['segment_type']
    ),
    'ghg_summary': DatasetConfig(
        name='GHG Summary',
        path_pattern='ghg_summary_*.csv',
        key_id_col='company_id',
        required_cols=['company_name', 'scope1_tco2e', 'scope2_tco2e', 'scope3_tco2e'],
        numeric_cols=['scope1_tco2e', 'scope2_tco2e', 'scope3_tco2e', 'total_tco2e'],
        categorical_cols=['sector', 'verification_status']
    ),
    'narrative': DatasetConfig(
        name='Narrative Reports',
        path_pattern='narrative_*.csv',
        key_id_col='narrative_id',
        required_cols=['company_name', 'scope1_tco2e', 'total_tco2e'],
        numeric_cols=['scope1_tco2e', 'total_tco2e', 'intensity'],
        categorical_cols=['sector', 'nse_code']
    ),
    'policy_sim': DatasetConfig(
        name='Policy Simulations',
        path_pattern='policy_sim_*.csv',
        key_id_col='sim_id',
        required_cols=['ev_mandate_pct', 'emissions_reduction_pct'],
        numeric_cols=['ev_mandate_pct', 'fuel_economy_std_pct', 'emissions_reduction_pct'],
        categorical_cols=['scenario_name']
    ),
}


class DatasetLoader:
    """Loads and validates datasets"""
    
    def __init__(self):
        self.data = {}
        self.metadata = {}
        self.validation_report = {}
    
    def load_dataset_type(self, dataset_type: str, split: Optional[str] = None) -> pd.DataFrame:
        """Load a specific dataset type (e.g., 'fuel_card', optionally filtered by 'train' or 'test')"""
        config = DATASET_CONFIGS.get(dataset_type)
        if config is None:
            raise ValueError(f"Unknown dataset type: {dataset_type}")
        
        pattern = config.path_pattern
        if split:
            pattern = pattern.replace('*', split)
        
        files = list(dataset_dir.glob(pattern))
        if not files:
            raise FileNotFoundError(f"No files matching pattern: {pattern}")
        
        dfs = []
        for file in files:
            df = pd.read_csv(file)
            dfs.append(df)
            logger.info(f"[LOAD] {file.name} ({len(df)} rows)")
        
        combined = pd.concat(dfs, ignore_index=True)
        self.data[dataset_type] = combined
        self._validate_dataset(dataset_type)
        
        return combined
    
    def load_all(self) -> Dict[str, pd.DataFrame]:
        """Load all dataset types"""
        for dtype in DATASET_CONFIGS.keys():
            try:
                self.load_dataset_type(dtype)
            except Exception as e:
                logger.error(f"Failed to load {dtype}: {e}")
        
        return self.data
    
    def _validate_dataset(self, dataset_type: str):
        """Validate dataset completeness and quality"""
        df = self.data[dataset_type]
        config = DATASET_CONFIGS[dataset_type]
        
        report = {
            'dataset': dataset_type,
            'rows': len(df),
            'columns': len(df.columns),
            'issues': [],
        }
        
        # Check required columns
        missing_cols = [col for col in config.required_cols if col not in df.columns]
        if missing_cols:
            report['issues'].append(f"Missing required columns: {missing_cols}")
        
        # Check for missing values
        missing_pct = (df.isnull().sum() / len(df) * 100)
        high_missing = missing_pct[missing_pct > 10]
        if len(high_missing) > 0:
            report['issues'].append(f"Columns with >10% missing: {high_missing.to_dict()}")
        
        # Check for duplicates
        if len(df) > len(df.drop_duplicates()):
            duplicates = len(df) - len(df.drop_duplicates())
            report['issues'].append(f"Found {duplicates} duplicate rows")
        
        # Check data types
        numeric_missing = [col for col in config.numeric_cols if col not in df.columns]
        if numeric_missing:
            report['issues'].append(f"Missing numeric columns: {numeric_missing}")
        
        if report['issues']:
            logger.warning(f"Validation issues for {dataset_type}: {report['issues']}")
        else:
            logger.info(f"[OK] {dataset_type} passed validation")
        
        self.validation_report[dataset_type] = report
    
    def get_validation_summary(self) -> str:
        """Get validation summary report"""
        summary = "DATA VALIDATION SUMMARY\n" + "=" * 80 + "\n"
        
        total_datasets = len(self.validation_report)
        passed = sum(1 for r in self.validation_report.values() if not r['issues'])
        failed = total_datasets - passed
        
        summary += f"Datasets: {total_datasets} ([PASS] {passed} passed, [FAIL] {failed} failed)\n\n"
        
        for dtype, report in self.validation_report.items():
            status = "[PASS]" if not report['issues'] else "[FAIL]"
            summary += f"{status} | {dtype:<20} | {report['rows']:>8,} rows x {report['columns']:>3} cols"
            if report['issues']:
                summary += f"\n       Issues: {'; '.join(report['issues'][:2])}"
            summary += "\n"
        
        return summary


class DatasetAnalyzer:
    """Analyzes loaded datasets"""
    
    def __init__(self, loader: DatasetLoader):
        self.loader = loader
    
    def get_emission_stats(self) -> Dict:
        """Get emission statistics across datasets"""
        stats = {}
        
        for dtype, df in self.loader.data.items():
            emission_cols = [col for col in df.columns if 'emission' in col.lower() or 'tco2e' in col.lower()]
            
            if emission_cols:
                stats[dtype] = {
                    'count': len(df),
                    'emission_cols': emission_cols,
                }
                
                for col in emission_cols:
                    if col in df.columns and df[col].dtype in ['float64', 'int64']:
                        stats[dtype][col] = {
                            'mean': df[col].mean(),
                            'min': df[col].min(),
                            'max': df[col].max(),
                            'total': df[col].sum(),
                        }
        
        return stats
    
    def get_company_stats(self) -> Dict:
        """Get statistics by company"""
        company_stats = {}
        
        for dtype, df in self.loader.data.items():
            if 'company_name' in df.columns:
                for company in df['company_name'].unique():
                    if company not in company_stats:
                        company_stats[company] = {'datasets': []}
                    
                    company_data = df[df['company_name'] == company]
                    company_stats[company]['datasets'].append({
                        'type': dtype,
                        'records': len(company_data),
                    })
        
        return company_stats
    
    def get_sector_stats(self) -> Dict:
        """Get statistics by sector"""
        sector_stats = {}
        
        for dtype, df in self.loader.data.items():
            if 'sector' in df.columns:
                sector_summary = df.groupby('sector').size().to_dict()
                
                emission_cols = [col for col in df.columns if 'tco2e' in col.lower()]
                for col in emission_cols:
                    if col in df.columns:
                        sector_summary[f'{col}_total'] = df.groupby('sector')[col].sum().to_dict()
                
                if dtype not in sector_stats:
                    sector_stats[dtype] = sector_summary
        
        return sector_stats


def print_analysis_report(loader: DatasetLoader, analyzer: DatasetAnalyzer):
    """Print comprehensive analysis report"""
    print("\n" + "=" * 100)
    print("INGESTION & ANALYSIS REPORT")
    print("=" * 100)
    
    # Validation
    print("\n" + loader.get_validation_summary())
    
    # Emission Stats
    print("\n[STATS] EMISSION STATISTICS:")
    print("-" * 100)
    emission_stats = analyzer.get_emission_stats()
    
    total_emissions = 0
    for dtype, stats in emission_stats.items():
        if 'emission_tco2e' in stats:
            total = stats['emission_tco2e'].get('total', 0)
            total_emissions += total
            print(f"  * {dtype:<20} {total:>15,.2f} tCO2e ({stats['count']:>6,} records)")
    
    print(f"\n  {'TOTAL':<20} {total_emissions:>15,.2f} tCO2e")
    
    # Company coverage
    print("\n[COMPANIES] COMPANY COVERAGE:")
    company_stats = analyzer.get_company_stats()
    print(f"  * Unique Companies: {len(company_stats):,}")
    print(f"  * Total Records: {sum(len(v['datasets']) for v in company_stats.values()):,}")
    
    # Sector coverage
    print("\n[SECTORS] SECTOR COVERAGE:")
    sector_stats = analyzer.get_sector_stats()
    all_sectors = set()
    for dtype_sectors in sector_stats.values():
        if isinstance(dtype_sectors, dict):
            all_sectors.update(k for k in dtype_sectors.keys() if not k.endswith('_total'))
    print(f"  * Unique Sectors: {len(all_sectors)}")
    print(f"  * Sectors: {', '.join(sorted(all_sectors)[:8])}{'...' if len(all_sectors) > 8 else ''}")
    
    print("\n" + "=" * 100)


# Main usage example
if __name__ == "__main__":
    print("[*] Loading datasets...")
    loader = DatasetLoader()
    loader.load_all()
    
    print("\n[*] Analyzing datasets...")
    analyzer = DatasetAnalyzer(loader)
    
    print_analysis_report(loader, analyzer)
