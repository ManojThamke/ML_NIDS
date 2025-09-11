import pandas as pd
from sklearn.model_selection import train_test_split

# Input cleaned dataset
input_file = '../data/cicids2017/cicids2017_cleaned.csv'
output_file = "./data/baseline_train.csv"

print("Loading cleaned dataset...")
df = pd.read_csv(input_file)

# Fix colum names
df.columns = df.columns.str.strip()

# Select 4 baseline features + label
features = ['Destination Port', 'Flow Duration', 'Fwd Packet Length Min', 'Packet Length Std']
label = 'Label'

df_baseline = df[features + [label]]

print("Selected baseline features:", features)
print("using label column:", label)

# Split dataset (70% train, 30% test)
train, test = train_test_split(df_baseline, test_size=0.3, random_state=42, stratify=df_baseline[label])

# Save to csv
train.to_csv("../data/baseline_train.csv", index=False)
test.to_csv("../data/baseline_test.csv", index=False)

print("Saved baseline_train.csv and baseline_test.csv")
print("Train shape:", train.shape, "| Test shape:", test.shape)