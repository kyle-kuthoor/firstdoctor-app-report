# FirstDoctor App Growth Report

## Overview
An automated Python script that combines 15 months of Google Play Console 
and App Store Connect data to generate a comprehensive cross-platform app 
growth report for management review.

## What it produces
- Monthly installs — Android vs iOS side by side
- Active device growth over time (Android)
- Month-over-month growth rate
- Daily install trend — Android vs iOS
- Text summary with key metrics
- PDF report ready for management presentation

## Key findings (March 2025 - May 2026)
- 7,656 total combined downloads (6,522 Android + 1,134 iOS)
- Peak month: December 2025 (1,679 Android installs)
- Biggest growth: November 2025 (+490.6% MoM)
- April 2026 cross-platform surge: 854 Android + 330 iOS
- 2,471 active devices maintained despite install fluctuations

## Usage
Place Google Play Console CSV files and App Store Connect CSV in the 
folder and run:
python app_report.py
## Tools
Python, Pandas, Matplotlib, Seaborn

## Context
Built for internal use at FirstDoctor, a telemedicine startup in Sri Lanka.
Raw data files are not included in this repository.
