import pandas as pd
import glob

# Load and combine all CSV files
files = glob.glob("stats-installs*.csv")
files.sort()

print(f"Found {len(files)} files:")
for f in files:
    print(f"  - {f}")

dfs = []
for f in files:
    df = pd.read_csv(f, encoding='utf-16')
    dfs.append(df)

# Combine into one dataset
combined = pd.concat(dfs, ignore_index=True)
combined['Date'] = pd.to_datetime(combined['Date'])
combined = combined.sort_values('Date').reset_index(drop=True)

print(f"\nTotal rows: {len(combined)}")
print(f"Date range: {combined['Date'].min().date()} to {combined['Date'].max().date()}")
print(f"\nColumns: {combined.columns.tolist()}")
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_theme(style="whitegrid")

# Build monthly summary
combined['Month'] = combined['Date'].dt.to_period('M')
monthly = combined.groupby('Month').agg(
    Total_Installs=('Daily Device Installs', 'sum'),
    Total_Uninstalls=('Daily Device Uninstalls', 'sum'),
    Total_User_Installs=('Daily User Installs', 'sum'),
    Peak_Active_Devices=('Active Device Installs', 'max')
).reset_index()

# Calculate month-over-month growth rate
monthly['MoM_Growth'] = monthly['Total_Installs'].pct_change() * 100

# Convert Month to string for cleaner labels
monthly['Month_Label'] = monthly['Month'].astype(str)

print("\nMonthly Summary:")
print(monthly[['Month_Label', 'Total_Installs', 'Total_Uninstalls', 
               'Peak_Active_Devices', 'MoM_Growth']].to_string(index=False))
fig, axes = plt.subplots(2, 2, figsize=(18, 12))
fig.suptitle("FirstDoctor App — Growth Report\nMarch 2025 to May 2026", 
             fontsize=18, fontweight="bold", y=1.02)

months = monthly['Month_Label']
x = range(len(months))

# ── CHART 1: Monthly installs ────────────────────────────────
axes[0,0].bar(x, monthly['Total_Installs'], 
              color=sns.color_palette("YlGn", len(monthly)))
axes[0,0].set_xticks(x)
axes[0,0].set_xticklabels(months, rotation=45, ha="right", fontsize=8)
axes[0,0].set_title("Monthly Device Installs", fontsize=13)
axes[0,0].set_ylabel("Installs")
for i, v in enumerate(monthly['Total_Installs']):
    axes[0,0].text(i, v + 10, str(v), ha="center", fontsize=7)

# ── CHART 2: Active devices growth ──────────────────────────
axes[0,1].plot(x, monthly['Peak_Active_Devices'], 
               color="#4a7c3f", linewidth=2.5, marker="o", markersize=5)
axes[0,1].fill_between(x, monthly['Peak_Active_Devices'], alpha=0.15, color="#4a7c3f")
axes[0,1].set_xticks(x)
axes[0,1].set_xticklabels(months, rotation=45, ha="right", fontsize=8)
axes[0,1].set_title("Active Device Installs Over Time", fontsize=13)
axes[0,1].set_ylabel("Active Devices")

# ── CHART 3: Month-over-month growth rate ───────────────────
colors = ["#e05c3a" if v < 0 else "#6b9e4e" for v in monthly['MoM_Growth'].fillna(0)]
axes[1,0].bar(x, monthly['MoM_Growth'].fillna(0), color=colors)
axes[1,0].axhline(0, color="black", linewidth=0.8, linestyle="--")
axes[1,0].set_xticks(x)
axes[1,0].set_xticklabels(months, rotation=45, ha="right", fontsize=8)
axes[1,0].set_title("Month-over-Month Growth Rate (%)", fontsize=13)
axes[1,0].set_ylabel("Growth %")

# ── CHART 4: Daily installs trend ───────────────────────────
axes[1,1].plot(combined['Date'], combined['Daily Device Installs'],
               color="#4a7c3f", linewidth=1, alpha=0.7)
axes[1,1].set_title("Daily Install Trend", fontsize=13)
axes[1,1].set_ylabel("Daily Installs")
axes[1,1].tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.savefig("firstdoctor_app_report.png", dpi=150, bbox_inches="tight")
plt.close()
print("\nReport saved as firstdoctor_app_report.png")
# ── TEXT SUMMARY ────────────────────────────────────────────
best_month = monthly.loc[monthly['Total_Installs'].idxmax()]
worst_month = monthly.loc[monthly['Total_Installs'].idxmin()]
best_growth = monthly.loc[monthly['MoM_Growth'].idxmax()]
worst_growth = monthly.loc[monthly['MoM_Growth'].idxmin()]
total_installs = monthly['Total_Installs'].sum()
peak_active = monthly['Peak_Active_Devices'].max()
latest_active = monthly['Peak_Active_Devices'].iloc[-1]

print("\n" + "=" * 55)
print("FIRSTDOCTOR APP — GROWTH REPORT SUMMARY")
print("March 2025 to May 2026")
print("=" * 55)
print(f"\nTotal installs (15 months):     {total_installs:,}")
print(f"Peak active devices:            {peak_active:,} (Jan 2026)")
print(f"Current active devices:         {latest_active:,}")
print(f"\nBest month:                     {best_month['Month_Label']} ({int(best_month['Total_Installs']):,} installs)")
print(f"Lowest month:                   {worst_month['Month_Label']} ({int(worst_month['Total_Installs']):,} installs)")
print(f"\nBiggest growth month:           {best_growth['Month_Label']} (+{best_growth['MoM_Growth']:.1f}%)")
print(f"Biggest drop month:             {worst_growth['Month_Label']} ({worst_growth['MoM_Growth']:.1f}%)")
print(f"\nKey observation:")
print(f"  Active devices remain at {latest_active:,} despite install fluctuations,")
print(f"  indicating strong user retention across the platform.")
print("=" * 55)
