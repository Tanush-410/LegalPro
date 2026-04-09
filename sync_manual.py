#!/usr/bin/env python3
"""
Simple Manual Sync
Run this anytime to sync new cases from the website
"""

import sys
sys.path.insert(0, "/Volumes/PortableSSD/court-ecosystem")

from daily_sync_scheduler import KarnatakaHCDailySync

if __name__ == "__main__":
    print("🔄 Starting manual sync...")
    syncer = KarnatakaHCDailySync()
    syncer.run_daily_sync()
    print("\n✅ Manual sync complete!")
