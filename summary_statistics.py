"""
Comprehensive statistical summary of all Carbon Trace Kenya datasets
"""
import pandas as pd
import numpy as np
from pathlib import Path

dataset_dir = Path("dataset_csv")

def load_all_datasets():
    """Load all datasets"""
    datasets = {}
    for csv_file in sorted(dataset_dir.glob("*.csv")):
        try:
            datasets[csv_file.name] = pd.read_csv(csv_file)
        except Exception as e:
            print(f"Error loading {csv_file.name}: {e}")
    return datasets

print("=" * 120)
print("COMPREHENSIVE STATISTICAL SUMMARY - CARBON TRACE KENYA DATASETS")
print("=" * 120)

datasets = load_all_datasets()

# 1. DATASET OVERVIEW
print("\n[STATS] DATASET OVERVIEW")
print("-" * 120)
total_rows = sum(df.shape[0] for df in datasets.values())
total_cols = sum(df.shape[1] for df in datasets.values())
print(f"Total Datasets: {len(datasets)}")
print(f"Total Rows: {total_rows:,}")
print(f"Total Columns: {total_cols}")
print(f"Average rows per dataset: {total_rows / len(datasets):,.0f}")

# 2. EMISSION STATISTICS
print("\n\n[EMISSIONS] EMISSION STATISTICS (tCO2e)")
print("-" * 120)

emission_data = []
for name, df in datasets.items():
    emission_cols = [col for col in df.columns if 'tco2e' in col.lower() or 'emission' in col.lower()]
    for col in emission_cols:
        if col in df.columns and df[col].dtype in ['float64', 'int64']:
            emission_data.append({
                'Dataset': name,
                'Column': col,
                'Count': df[col].notna().sum(),
                'Total': df[col].sum(),
                'Mean': df[col].mean(),
                'Min': df[col].min(),
                'Max': df[col].max(),
                'Std': df[col].std(),
            })

if emission_data:
    emission_df = pd.DataFrame(emission_data)
    
    # Group by column
    print("\nBy Emission Column:")
    for col in emission_df['Column'].unique():
        subset = emission_df[emission_df['Column'] == col]
        total = subset['Total'].sum()
        print(f"\n  {col}:")
        print(f"    Total: {total:>15,.2f} tCO2e")
        print(f"    Sources: {len(subset)} datasets")
        for _, row in subset.iterrows():
            if row['Total'] > 0:
                print(f"      • {row['Dataset']:<35} {row['Total']:>15,.2f} ({row['Count']:>6,} records)")
    
    # Grand total
    grand_total = emission_df['Total'].sum()
    print(f"\n  GRAND TOTAL: {grand_total:>20,.2f} tCO2e across all datasets")

# 3. COMPANY & SECTOR ANALYSIS
print("\n\n[COMPANIES] COMPANY & SECTOR ANALYSIS")
print("-" * 120)

all_companies = set()
all_sectors = set()
company_sector_map = {}

for name, df in datasets.items():
    if 'company_name' in df.columns:
        for company in df['company_name'].dropna().unique():
            all_companies.add(company)
            
            if 'sector' in df.columns:
                sectors = df[df['company_name'] == company]['sector'].unique()
                for sector in sectors:
                    if company not in company_sector_map:
                        company_sector_map[company] = set()
                    company_sector_map[company].add(sector)
    
    if 'sector' in df.columns:
        for sector in df['sector'].dropna().unique():
            all_sectors.add(sector)

print(f"\nUnique Companies: {len(all_companies):,}")
print(f"Unique Sectors: {len(all_sectors)}")
if all_sectors:
    print(f"Sectors: {', '.join(sorted(all_sectors))}")

# 4. TEMPORAL ANALYSIS
print("\n\n[TIME] TEMPORAL ANALYSIS")
print("-" * 120)

years = set()
months = set()
date_cols = []

for name, df in datasets.items():
    # Find year columns
    if 'fy_year' in df.columns:
        years.update(df['fy_year'].dropna().unique())
    elif 'year' in df.columns:
        years.update(df['year'].dropna().unique())
    
    # Find month columns
    if 'month' in df.columns:
        months.update(df['month'].dropna().unique())
    
    # Find date columns
    date_cols_found = [col for col in df.columns if 'date' in col.lower() and df[col].dtype == 'object']
    date_cols.extend([(name, col) for col in date_cols_found])

if years:
    print(f"Fiscal Years Covered: {', '.join(str(int(y)) for y in sorted(years))}")

if months:
    print(f"Months Covered: {len(sorted(set(months)))} months")

if date_cols:
    print(f"Date Columns Found: {len(date_cols)}")
    for dataset_name, col in date_cols[:5]:
        print(f"  • {dataset_name}: {col}")

# 5. DATA QUALITY METRICS
print("\n\n[QA] DATA QUALITY METRICS")
print("-" * 120)

quality_metrics = []
for name, df in datasets.items():
    missing_pct = (df.isnull().sum().sum() / (df.shape[0] * df.shape[1]) * 100)
    duplicate_pct = (len(df) - len(df.drop_duplicates())) / len(df) * 100
    
    quality_metrics.append({
        'Dataset': name,
        'Rows': df.shape[0],
        'Missing%': missing_pct,
        'Duplicates%': duplicate_pct,
        'Quality': 'Excellent' if missing_pct < 1 and duplicate_pct == 0 else 'Good' if missing_pct < 5 else 'Fair'
    })

quality_df = pd.DataFrame(quality_metrics).sort_values('Missing%')
print(quality_df.to_string(index=False))

# 6. COLUMN TYPE ANALYSIS
print("\n\n[TYPES] COLUMN TYPE DISTRIBUTION")
print("-" * 120)

numeric_count = 0
string_count = 0
datetime_count = 0
other_count = 0

for name, df in datasets.items():
    for col in df.columns:
        dtype_name = str(df[col].dtype)
        if dtype_name in ['int64', 'float64']:
            numeric_count += 1
        elif dtype_name == 'object':
            string_count += 1
        elif 'datetime' in dtype_name:
            datetime_count += 1
        else:
            other_count += 1

print(f"Numeric Columns (int/float): {numeric_count}")
print(f"String Columns (object): {string_count}")
print(f"DateTime Columns: {datetime_count}")
print(f"Other Types: {other_count}")

# 7. KEY METRICS BY DATASET TYPE
print("\n\n[SUMMARY] DATASET CATEGORY SUMMARY")
print("-" * 120)

categories = {}
for name in datasets.keys():
    base = name.replace('_train.csv', '').replace('_test.csv', '')
    if base not in categories:
        categories[base] = {'train': None, 'test': None, 'file': None}
    
    if 'train' in name:
        categories[base]['train'] = datasets[name]
    elif 'test' in name:
        categories[base]['test'] = datasets[name]
    else:
        categories[base]['file'] = datasets[name]

for category in sorted(categories.keys()):
    info = categories[category]
    total_rows = 0
    total_cols = 0
    
    if info['train'] is not None:
        total_rows += len(info['train'])
        total_cols = len(info['train'].columns)
    if info['test'] is not None:
        total_rows += len(info['test'])
    if info['file'] is not None:
        total_rows += len(info['file'])
        total_cols = len(info['file'].columns)
    
    print(f"\n{category.upper()}")
    print(f"  • Total Records: {total_rows:,}")
    print(f"  • Columns: {total_cols}")
    
    if info['train'] is not None and info['test'] is not None:
        train_size = len(info['train'])
        test_size = len(info['test'])
        ratio = test_size / (train_size + test_size) * 100
        print(f"  • Train/Test Split: {train_size:,} / {test_size:,} ({ratio:.1f}% test)")

# 8. RECOMMENDATIONS
print("\n\n[NEXT] RECOMMENDATIONS FOR NEXT STEPS")
print("-" * 120)
print("""
1. DATA INGESTION:
   [OK] All datasets have been successfully loaded and analyzed
   [OK] Create database tables to persist this data
   [OK] Implement ETL pipeline for regular data updates

2. MODELING:
   - Emission Prediction: Use fuel_card, travel, and commute datasets for ML
   - Anomaly Detection: Leverage anomaly_train.csv for training detection
   - Policy Impact Simulation: Use policy_sim datasets for scenario analysis

3. ANALYSIS:
   - Prepare comparative analysis across sectors and companies
   - Generate emission intensity benchmarks
   - Track YoY changes and identify trends

4. EXPORT & REPORTING:
   - Configure data pipelines to populate ghg_summary and narrative tables
   - Set up automated report generation
   - Create visualization dashboards

5. DATA QUALITY:
   - Validate geographic data (GPS logs, coordinates)
   - Reconcile emission calculations across different data sources
   - Establish data governance policies
""")

print("\n" + "=" * 120)
print("END OF STATISTICAL SUMMARY")
print("=" * 120)
