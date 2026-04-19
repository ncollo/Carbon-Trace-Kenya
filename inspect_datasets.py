import pandas as pd
import os
from pathlib import Path

dataset_dir = Path("dataset_csv")
csv_files = sorted(dataset_dir.glob("*.csv"))

print("=" * 80)
print("DATASET INSPECTION REPORT")
print("=" * 80)

for csv_file in csv_files:
    print(f"\n{'='*80}")
    print(f"FILE: {csv_file.name}")
    print(f"{'='*80}")
    
    df = pd.read_csv(csv_file)
    
    # Schema
    print(f"\n📋 SCHEMA ({len(df.columns)} columns):")
    print(df.dtypes)
    
    # Shape
    print(f"\n📊 SHAPE: {df.shape[0]} rows × {df.shape[1]} columns")
    
    # Missing values
    missing = df.isnull().sum()
    if missing.sum() > 0:
        print(f"\n⚠️  MISSING VALUES:")
        print(missing[missing > 0])
    else:
        print(f"\n✓ No missing values")
    
    # Sample rows
    print(f"\n📖 FIRST 3 ROWS:")
    print(df.head(3).to_string())
    
    # Basic statistics
    print(f"\n📈 NUMERIC SUMMARY:")
    numeric_cols = df.select_dtypes(include=['number']).columns
    if len(numeric_cols) > 0:
        print(df[numeric_cols].describe().to_string())
    else:
        print("No numeric columns")
    
    # Categorical summary
    categorical_cols = df.select_dtypes(include=['object']).columns
    if len(categorical_cols) > 0:
        print(f"\n🏷️  CATEGORICAL SUMMARY:")
        for col in categorical_cols[:3]:  # Show first 3 categorical cols
            unique_count = df[col].nunique()
            print(f"  {col}: {unique_count} unique values")
            if unique_count <= 10:
                print(f"    Values: {df[col].unique().tolist()}")

print("\n" + "=" * 80)
print("END OF REPORT")
print("=" * 80)
