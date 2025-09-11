import pandas as pd 
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF

# Input cleaned dataset
input_file = '../data/cicids2017/cicids2017_cleaned.csv'
df = pd.read_csv(input_file)

# 1. Class Distribution
plt.figure(figsize=(6,4))
df['Label'].value_counts().plot(kind='bar', color=['green', 'red'])
plt.title("Class Distribution (0=BENIGN, 1=ATTACK)")
plt.xlabel("Class")
plt.ylabel("Count")
plt.savefig("../docs/week 1/EDA/class_distribution.png")
plt.close()

# 2. Feature Distribution 
numeric_cols = df.select_dtypes(include='number').columns[:4]
for col in numeric_cols:
    plt.figure(figsize=(6,4))
    sns.histplot(df[col], bins=50, kde=True)
    plt.title(f"Distribution of {col}")
    plt.savefig(f"../docs/week 1/EDA/{col}_histogram.png")
    plt.close()

# 3. Correlation Heatmap
plt.figure(figsize=(12,8))
corr = df.corr(numeric_only=True)
sns.heatmap(corr, cmap="coolwarm", center=0)
plt.title("Feature Correlation Heatmap")
plt.savefig("../docs/week 1/EDA/correlation_heatmap.png")
plt.close()

# 4. Build PDF Report
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=14)
pdf.cell(200, 10, "EDA Report - ML_NIDS Project", ln=True, align='C')

pdf.set_font("Arial", size=12)
pdf.cell(200, 10, "Class Distribution", ln=True)
pdf.image("../docs/week 1/EDA/class_distribution.png", x=10, w=150)

for col in numeric_cols:
    pdf.cell(200, 10, f"2. Feature Distribution: {col}", ln=True)
    pdf.image(f"../docs/week 1/EDA/{col}_histogram.png", x=30, w=150)

pdf.cell(200, 10, "3. Correlation Heatmap", ln=True)
pdf.image("../docs/week 1/EDA/correlation_heatmap.png", x=10, w=190)

pdf.output("../docs/week 1/EDA/EDA_Report.pdf")
print("EDA Report generated: ../docs/week 1/EDA/EDA_Report.pdf")