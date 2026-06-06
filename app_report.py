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

# ── LOAD IOS DATA ────────────────────────────────────────────
ios_df = pd.read_csv("firstdoctor-first_time_downloads-20250401-20260603.csv", skiprows=2)
ios_df.columns = ["Date", "Downloads"]
ios_df = ios_df[ios_df["Date"].notna()]
ios_df = ios_df[ios_df["Date"] != "Date"]
ios_df["Date"] = pd.to_datetime(ios_df["Date"], format="%m/%d/%y")
ios_df["Downloads"] = pd.to_numeric(ios_df["Downloads"], errors="coerce").fillna(0).astype(int)
ios_df = ios_df.sort_values("Date").reset_index(drop=True)

print(f"iOS date range: {ios_df['Date'].min().date()} to {ios_df['Date'].max().date()}")
print(f"Total iOS downloads: {ios_df['Downloads'].sum():,}")


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
# ── BUILD iOS MONTHLY SUMMARY ────────────────────────────────
ios_df['Month'] = ios_df['Date'].dt.to_period('M')
ios_monthly = ios_df.groupby('Month')['Downloads'].sum().reset_index()
ios_monthly.columns = ['Month', 'iOS_Downloads']
ios_monthly['Month_Label'] = ios_monthly['Month'].astype(str)

# ── MERGE ANDROID AND iOS ────────────────────────────────────
combined_monthly = monthly.merge(ios_monthly[['Month_Label', 'iOS_Downloads']], 
                                  on='Month_Label', how='left')
combined_monthly['iOS_Downloads'] = combined_monthly['iOS_Downloads'].fillna(0).astype(int)
combined_monthly['Total_Combined'] = combined_monthly['Total_Installs'] + combined_monthly['iOS_Downloads']

print("\nCombined Platform Summary:")
print(combined_monthly[['Month_Label', 'Total_Installs', 'iOS_Downloads', 'Total_Combined']].to_string(index=False))
fig, axes = plt.subplots(2, 2, figsize=(18, 12))
fig.suptitle("FirstDoctor App — Growth Report\nMarch 2025 to May 2026", 
             fontsize=18, fontweight="bold", y=1.02)

months = monthly['Month_Label']
x = range(len(months))

# ── CHART 1: Android vs iOS monthly installs ─────────────────
bar_width = 0.35
x_pos = range(len(combined_monthly))

axes[0,0].bar([i - bar_width/2 for i in x_pos], combined_monthly['Total_Installs'],
              width=bar_width, label='Android', color='#4a7c3f', alpha=0.85)
axes[0,0].bar([i + bar_width/2 for i in x_pos], combined_monthly['iOS_Downloads'],
              width=bar_width, label='iOS', color='#7ab3f0', alpha=0.85)
axes[0,0].set_xticks(x_pos)
axes[0,0].set_xticklabels(combined_monthly['Month_Label'], rotation=45, ha='right', fontsize=8)
axes[0,0].set_title('Monthly Installs — Android vs iOS', fontsize=13)
axes[0,0].set_ylabel('Installs')
axes[0,0].legend(fontsize=8)

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
print(f"\niOS daily data sample:")
print(ios_df[['Date', 'Downloads']].tail(10))
print(f"iOS max daily: {ios_df['Downloads'].max()}")

# ── CHART 4: Daily trend — Android vs iOS ───────────────────
axes[1,1].plot(combined['Date'], combined['Daily Device Installs'],
               color='#4a7c3f', linewidth=1, alpha=0.8, label='Android')
axes[1,1].plot(ios_df['Date'], ios_df['Downloads'],
               color='#7ab3f0', linewidth=1, alpha=0.8, label='iOS')
axes[1,1].set_title('Daily Install Trend — Android vs iOS', fontsize=13)
axes[1,1].set_ylabel('Daily Installs')
axes[1,1].tick_params(axis='x', rotation=45)
axes[1,1].legend(fontsize=8)

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
total_ios = int(ios_df['Downloads'].sum())
total_combined = total_installs + total_ios

print(f"\nAndroid installs (15 months):   {total_installs:,}")
print(f"iOS downloads (14 months):      {total_ios:,}")
print(f"Total combined downloads:       {total_combined:,}")
print(f"Peak active devices:            {peak_active:,} (Jan 2026)")
print(f"Current active devices:         {latest_active:,}")
print(f"\nBest month (Android):           {best_month['Month_Label']} ({int(best_month['Total_Installs']):,} installs)")
print(f"Lowest month (Android):         {worst_month['Month_Label']} ({int(worst_month['Total_Installs']):,} installs)")
print(f"\nBiggest growth month:           {best_growth['Month_Label']} (+{best_growth['MoM_Growth']:.1f}%)")
print(f"Biggest drop month:             {worst_growth['Month_Label']} ({worst_growth['MoM_Growth']:.1f}%)")
print(f"\nKey observation:")
print(f"  Active devices remain at {latest_active:,} despite install fluctuations,")
print(f"  indicating strong user retention across the platform.")
print("=" * 55)
plt.tight_layout()
plt.savefig("firstdoctor_app_report_v2.png", dpi=150, bbox_inches="tight")
plt.close()
print("\nReport saved as firstdoctor_app_report_v2.png")