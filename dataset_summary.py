import pandas as pd
from pathlib import Path

dataset_dir = Path("dataset_csv")
csv_files = sorted(dataset_dir.glob("*.csv"))

print("DATASET INVENTORY & QUICK STATS")
print("=" * 100)
print(f"{'FILE':<35} {'ROWS':<10} {'COLS':<8} {'KEY COLUMNS':<45}")
print("-" * 100)

all_files_info = {}
for csv_file in csv_files:
    df = pd.read_csv(csv_file)
    cols = ", ".join(df.columns[:4]) + ("..." if len(df.columns) > 4 else "")
    print(f"{csv_file.name:<35} {df.shape[0]:<10} {df.shape[1]:<8} {cols:<45}")
    all_files_info[csv_file.name] = {
        'shape': df.shape,
        'columns': list(df.columns),
        'dtypes': df.dtypes.to_dict()
    }

print("\n" + "=" * 100)
print("DATASET CATEGORIES:")
print("-" * 100)

train_test = {}
for name in all_files_info.keys():
    base = name.replace('_train.csv', '').replace('_test.csv', '')
    if base not in train_test:
        train_test[base] = []
    train_test[base].append(name)

for base, files in sorted(train_test.items()):
    print(f"\n🔹 {base.upper()}")
    for f in files:
        rows = all_files_info[f]['shape'][0]
        print(f"   • {f:<35} ({rows} rows)")
