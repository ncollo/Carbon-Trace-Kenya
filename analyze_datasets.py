"""
Comprehensive dataset loader and analyzer for Carbon Trace Kenya.
Loads all datasets, provides statistics, and prepares data for ingestion.
"""
import pandas as pd
import numpy as np
from pathlib import Path
from collections import defaultdict
import json

dataset_dir = Path("dataset_csv")

class DatasetAnalyzer:
    def __init__(self):
        self.datasets = {}
        self.stats = {}
        self.issues = defaultdict(list)
        
    def load_all(self):
        """Load all CSV files from dataset_csv/"""
        csv_files = sorted(dataset_dir.glob("*.csv"))
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file)
                self.datasets[csv_file.name] = df
                print(f"[OK] Loaded {csv_file.name} ({df.shape[0]} rows x {df.shape[1]} cols)")
            except Exception as e:
                self.issues[csv_file.name].append(f"Load error: {e}")
                print(f"[FAIL] Failed to load {csv_file.name}: {e}")
    
    def analyze_all(self):
        """Analyze each dataset"""
        for name, df in self.datasets.items():
            self.stats[name] = self._analyze_dataset(name, df)
    
    def _analyze_dataset(self, name, df):
        """Analyze a single dataset"""
        stats = {
            'filename': name,
            'shape': df.shape,
            'columns': list(df.columns),
            'dtypes': df.dtypes.to_dict(),
            'missing_pct': (df.isnull().sum() / len(df) * 100).to_dict(),
            'duplicates': len(df) - len(df.drop_duplicates()),
            'numeric_cols': list(df.select_dtypes(include=[np.number]).columns),
            'categorical_cols': list(df.select_dtypes(include=['object']).columns),
        }
        
        # Numeric summary
        numeric_df = df.select_dtypes(include=[np.number])
        if len(numeric_df) > 0:
            stats['numeric_summary'] = numeric_df.describe().to_dict()
        
        # Check for key columns
        if 'company_name' in df.columns:
            stats['unique_companies'] = df['company_name'].nunique()
        if 'sector' in df.columns:
            stats['unique_sectors'] = df['sector'].nunique()
            stats['sectors'] = df['sector'].unique().tolist()
        if 'fy_year' in df.columns:
            stats['years'] = sorted(df['fy_year'].unique().tolist())
        
        # Data quality checks
        if df.isnull().sum().sum() > 0:
            self.issues[name].append(f"Missing values detected: {df.isnull().sum().sum()} cells")
        if stats['duplicates'] > 0:
            self.issues[name].append(f"Duplicate rows: {stats['duplicates']}")
        
        return stats
    
    def get_summary_report(self):
        """Generate a summary report"""
        print("\n" + "=" * 100)
        print("COMPREHENSIVE DATASET ANALYSIS REPORT")
        print("=" * 100)
        
        # Total statistics
        total_rows = sum(df.shape[0] for df in self.datasets.values())
        total_cols = sum(df.shape[1] for df in self.datasets.values())
        print(f"\n[STATS] OVERALL STATISTICS:")
        print(f"  • Total Datasets: {len(self.datasets)}")
        print(f"  • Total Rows: {total_rows:,}")
        print(f"  • Total Columns: {total_cols}")
        
        # Dataset breakdown
        print(f"\n[FILES] DATASET BREAKDOWN:")
        
        categories = defaultdict(list)
        for name in sorted(self.datasets.keys()):
            base = name.replace('_train.csv', '').replace('_test.csv', '')
            categories[base].append(name)
        
        for category in sorted(categories.keys()):
            print(f"\n  * {category.upper()}")
            for fname in categories[category]:
                df = self.datasets[fname]
                s = self.stats[fname]
                print(f"     • {fname:<35} {df.shape[0]:>8,} rows x {df.shape[1]:>3} cols", end="")
                if s['missing_pct']:
                    missing = sum(1 for v in s['missing_pct'].values() if v > 0)
                    if missing > 0:
                        print(f"  [WARN] {missing} cols w/ missing values")
                    else:
                        print()
                else:
                    print()
        
        # Key insights
        print(f"\n[INFO] KEY INSIGHTS:")
        
        # Companies
        all_companies = set()
        for df in self.datasets.values():
            if 'company_name' in df.columns:
                all_companies.update(df['company_name'].dropna().unique())
        print(f"  • Unique Companies: {len(all_companies):,}")
        
        # Sectors
        all_sectors = set()
        for df in self.datasets.values():
            if 'sector' in df.columns:
                all_sectors.update(df['sector'].dropna().unique())
        print(f"  • Unique Sectors: {len(all_sectors)}")
        print(f"    {', '.join(sorted(all_sectors)[:5])}{'...' if len(all_sectors) > 5 else ''}")
        
        # Years
        all_years = set()
        for df in self.datasets.values():
            if 'fy_year' in df.columns:
                all_years.update(df['fy_year'].dropna().unique())
        print(f"  • Fiscal Years: {', '.join(str(int(y)) for y in sorted(all_years))}")
        
        # Emissions data
        emission_cols = []
        for df in self.datasets.values():
            emission_cols.extend([col for col in df.columns if 'tco2e' in col.lower()])
        if emission_cols:
            print(f"  • Emission-related columns: {len(set(emission_cols))} unique")
        
        # Issues
        if self.issues:
            print(f"\n[WARN] DATA QUALITY ISSUES:")
            for fname, issue_list in sorted(self.issues.items()):
                for issue in issue_list:
                    print(f"     • {fname}: {issue}")
        else:
            print(f"\n[OK] No data quality issues detected!")
        
        print("\n" + "=" * 100)
    
    def get_detailed_schema(self, filename):
        """Get detailed schema for a specific file"""
        if filename not in self.datasets:
            return f"File {filename} not found"
        
        df = self.datasets[filename]
        s = self.stats[filename]
        
        print(f"\n{'=' * 100}")
        print(f"DETAILED SCHEMA: {filename}")
        print(f"{'=' * 100}")
        print(f"\nShape: {df.shape[0]} rows x {df.shape[1]} columns")
        print(f"\nColumns ({len(df.columns)}):")
        print("-" * 100)
        print(f"{'#':<3} {'Column Name':<30} {'Data Type':<15} {'Non-Null':<12} {'Unique':<10} {'Sample Values':<30}")
        print("-" * 100)
        
        for i, col in enumerate(df.columns, 1):
            dtype = str(df[col].dtype)
            non_null = df[col].notna().sum()
            unique = df[col].nunique()
            
            # Sample values
            if df[col].dtype == 'object':
                sample = ', '.join(str(v)[:15] for v in df[col].dropna().unique()[:2])
            else:
                sample = str(df[col].dropna().iloc[0] if len(df) > 0 else 'N/A')[:15]
            
            print(f"{i:<3} {col:<30} {dtype:<15} {non_null:<12} {unique:<10} {sample:<30}")
        
        # First 3 rows
        print(f"\nFirst 3 rows:")
        print(df.head(3).to_string())
        print()

# Main execution
if __name__ == "__main__":
    analyzer = DatasetAnalyzer()
    print("[*] Loading datasets...\n")
    analyzer.load_all()
    
    print("\n[*] Analyzing datasets...\n")
    analyzer.analyze_all()
    
    print("\n[*] Generating report...\n")
    analyzer.get_summary_report()
    
    # Show detailed schema for a few key files
    key_files = [
        'fuel_card_train.csv',
        'ghg_summary_train.csv',
        'narrative_train.csv',
        'travel_train.csv'
    ]
    
    for fname in key_files:
        if fname in analyzer.datasets:
            analyzer.get_detailed_schema(fname)
    
    print("\n[OK] Dataset Analysis Complete!")
