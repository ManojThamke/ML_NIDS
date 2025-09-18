# Features used — Day 16

Selected features (for initial experiments):

1. Destination Port
2. Flow Duration
3. Fwd Packet Length Min
4. Packet Length Std
5. Fwd Packet Length Mean
6. Bwd Packet Length Mean
7. Total Fwd Packets
8. Total Length of Fwd Packets

Preprocessing steps applied:

- Missing values imputed using median (SimpleImputer)
- Features standardized with StandardScaler (zero mean, unit variance)

Notes:
- If a preferred feature was not present in final_train.csv, it was replaced with the next available numeric column.
