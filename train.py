"""
train.py - EDA, preprocessing, pelatihan & evaluasi Regresi Linear Sederhana
Studi kasus: Prediksi Pendapatan Toko Es Krim (Revenue) dari Suhu (Temperature)
Dataset   : Kaggle - Ice Cream Revenue (IceCreamData.csv)
Jalankan  : python train.py
"""
import json
import os

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

DATA_PATH = os.path.join("data", "IceCreamData.csv")
MODEL_PATH = os.path.join("model", "model_regresi_linear.joblib")
METRICS_PATH = os.path.join("model", "metrics.json")
IMG_DIR = os.path.join("static", "img")
os.makedirs(IMG_DIR, exist_ok=True)
os.makedirs("model", exist_ok=True)

sns.set_theme(style="whitegrid")

# ------------------------------------------------------------------ 1. LOAD
if not os.path.exists(DATA_PATH):
    raise SystemExit(
        f"File {DATA_PATH} tidak ditemukan.\n"
        "Unduh dari Kaggle (Ice Cream Revenue) lalu taruh di folder data/ "
        "dengan nama IceCreamData.csv. Lihat data/README.md."
    )

df = pd.read_csv(DATA_PATH)
df.columns = [c.strip() for c in df.columns]
print("Bentuk data :", df.shape)
print(df.head())
print(df.info())
print(df.describe())

# ---------------------------------------------------------- 2. PRA-PEMROSESAN
n_awal = len(df)
df = df[["Temperature", "Revenue"]].apply(pd.to_numeric, errors="coerce")
n_missing = int(df.isna().sum().sum())
df = df.dropna()
n_duplikat = int(df.duplicated().sum())
df = df.drop_duplicates()

# Outlier: aturan IQR pada residual kasar tidak dipakai; cukup IQR per kolom
def iqr_bounds(s, k=1.5):
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    iqr = q3 - q1
    return q1 - k * iqr, q3 + k * iqr

lo_t, hi_t = iqr_bounds(df["Temperature"])
lo_r, hi_r = iqr_bounds(df["Revenue"])
mask_out = (
    (df["Temperature"] < lo_t) | (df["Temperature"] > hi_t)
    | (df["Revenue"] < lo_r) | (df["Revenue"] > hi_r)
)
n_outlier = int(mask_out.sum())
# Pendapatan negatif tidak masuk akal secara bisnis -> hapus
n_negatif = int((df["Revenue"] < 0).sum())
df = df[~mask_out & (df["Revenue"] >= 0)].reset_index(drop=True)
print(f"Missing={n_missing}, duplikat={n_duplikat}, outlier IQR={n_outlier}, "
      f"revenue negatif={n_negatif}, data akhir={len(df)}")

corr = float(df["Temperature"].corr(df["Revenue"]))
print("Korelasi Pearson:", round(corr, 4))

# ------------------------------------------------------------------- 3. EDA
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
sns.histplot(df["Temperature"], kde=True, ax=axes[0], color="#0d6efd")
axes[0].set_title("Distribusi Temperature (°C)")
sns.histplot(df["Revenue"], kde=True, ax=axes[1], color="#fd7e14")
axes[1].set_title("Distribusi Revenue (USD)")
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, "distribusi.png"), dpi=130)
plt.close()

plt.figure(figsize=(6.5, 4.5))
sns.scatterplot(data=df, x="Temperature", y="Revenue", alpha=0.6, color="#0d6efd")
plt.title(f"Scatterplot Temperature vs Revenue (r = {corr:.3f})")
plt.xlabel("Temperature (°C)")
plt.ylabel("Revenue (USD)")
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, "scatter.png"), dpi=130)
plt.close()

# ----------------------------------------------------------------- 4. MODEL
X = df[["Temperature"]]
y = df["Revenue"]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = LinearRegression()
model.fit(X_train, y_train)

y_pred_train = model.predict(X_train)
y_pred_test = model.predict(X_test)

r2_train = r2_score(y_train, y_pred_train)
r2_test = r2_score(y_test, y_pred_test)
rmse_train = float(np.sqrt(mean_squared_error(y_train, y_pred_train)))
rmse_test = float(np.sqrt(mean_squared_error(y_test, y_pred_test)))
mae_test = float(mean_absolute_error(y_test, y_pred_test))

intercept = float(model.intercept_)
coef = float(model.coef_[0])

print(f"Intersep (b0) : {intercept:.4f}")
print(f"Koefisien (b1): {coef:.4f}")
print(f"R2  train/test: {r2_train:.4f} / {r2_test:.4f}")
print(f"RMSE train/test: {rmse_train:.4f} / {rmse_test:.4f}")
print(f"MAE test      : {mae_test:.4f}")

# Garis regresi
plt.figure(figsize=(6.5, 4.5))
plt.scatter(X_train, y_train, alpha=0.4, label="Data latih", color="#6c757d")
plt.scatter(X_test, y_test, alpha=0.7, label="Data uji", color="#0d6efd")
xs = np.linspace(X["Temperature"].min(), X["Temperature"].max(), 100).reshape(-1, 1)
plt.plot(xs, model.predict(pd.DataFrame(xs, columns=["Temperature"])),
         color="#dc3545", lw=2, label="Garis regresi")
plt.xlabel("Temperature (°C)")
plt.ylabel("Revenue (USD)")
plt.title("Garis Regresi Linear")
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, "regresi.png"), dpi=130)
plt.close()

# Residual
resid = y_test - y_pred_test
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
axes[0].scatter(y_pred_test, resid, alpha=0.6, color="#0d6efd")
axes[0].axhline(0, color="#dc3545", ls="--")
axes[0].set_xlabel("Revenue prediksi")
axes[0].set_ylabel("Residual")
axes[0].set_title("Residual vs Prediksi")
sns.histplot(resid, kde=True, ax=axes[1], color="#198754")
axes[1].set_title("Distribusi Residual")
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, "residual.png"), dpi=130)
plt.close()

# ------------------------------------------------------------ 5. PERSISTENCE
joblib.dump(model, MODEL_PATH)

metrics = {
    "n_awal": n_awal,
    "n_missing": n_missing,
    "n_duplikat": n_duplikat,
    "n_outlier": n_outlier,
    "n_negatif": n_negatif,
    "n_akhir": int(len(df)),
    "n_train": int(len(X_train)),
    "n_test": int(len(X_test)),
    "korelasi": corr,
    "intercept": intercept,
    "coef": coef,
    "r2_train": float(r2_train),
    "r2_test": float(r2_test),
    "rmse_train": rmse_train,
    "rmse_test": rmse_test,
    "mae_test": mae_test,
    "temp_min": float(df["Temperature"].min()),
    "temp_max": float(df["Temperature"].max()),
    "temp_mean": float(df["Temperature"].mean()),
    "rev_min": float(df["Revenue"].min()),
    "rev_max": float(df["Revenue"].max()),
    "rev_mean": float(df["Revenue"].mean()),
    "desc": df.describe().round(3).to_dict(),
}
with open(METRICS_PATH, "w", encoding="utf-8") as f:
    json.dump(metrics, f, indent=2)
print("Model & metrik tersimpan di folder model/")
