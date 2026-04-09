#!/usr/bin/env python3

import sqlite3

conn = sqlite3.connect('/Volumes/PortableSSD/court-ecosystem/court_cases.db')
cur = conn.cursor()

# Get all statistics
cur.execute('SELECT COUNT(*) FROM cases')
total_cases = cur.fetchone()[0]

cur.execute('SELECT COUNT(DISTINCT judge_name) FROM judgments WHERE judge_name IS NOT NULL')
total_judges = cur.fetchone()[0]

cur.execute('SELECT COUNT(*) FROM hearing_dates')
total_hearings = cur.fetchone()[0]

cur.execute('SELECT COUNT(*) FROM case_appeals')
total_appeals = cur.fetchone()[0]

cur.execute('SELECT COUNT(*) FROM case_timeline')
total_timeline = cur.fetchone()[0]

print('📊 DATABASE STATISTICS')
print('=' * 50)
print(f'Cases: {total_cases}')
print(f'Judges: {total_judges}')
print(f'Hearing Dates: {total_hearings}')
print(f'Appeals Tracked: {total_appeals}')
print(f'Timeline Events: {total_timeline}')
print('=' * 50)

conn.close()
