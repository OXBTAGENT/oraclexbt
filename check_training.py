#!/usr/bin/env python3
"""Monitor the training session progress"""

import json
import glob
import os
from datetime import datetime

# Find most recent training results file
results_files = sorted(glob.glob("training_results_*.json"), reverse=True)

if not results_files:
    print("🔄 Training in progress... No results file yet.")
    print("   Check back in a few minutes.")
else:
    latest = results_files[0]
    print(f"\n📊 Latest Training Results: {latest}\n")
    
    with open(latest, 'r') as f:
        data = json.load(f)
    
    print(f"Session ID: {data['session_id']}")
    print(f"Timestamp: {data['timestamp']}")
    print(f"\nTotal Tests: {data['total_tests']}")
    print(f"✅ Passed: {data['passed']} ({data['passed']/data['total_tests']*100:.1f}%)")
    print(f"❌ Failed: {data['failed']} ({data['failed']/data['total_tests']*100:.1f}%)")
    
    if data['failed'] > 0:
        print("\n⚠️  Failed Tests:")
        for result in data['results']:
            if not result['passed']:
                print(f"  • {result['test']}")
                print(f"    {result['notes']}")
    
    print("\n" + "="*60)
    
    if data['passed'] / data['total_tests'] >= 0.8:
        print("🎉 Status: EXCELLENT - Agent ready for production!")
    elif data['passed'] / data['total_tests'] >= 0.6:
        print("✅ Status: GOOD - Agent is functional")
    else:
        print("⚠️  Status: NEEDS IMPROVEMENT")
