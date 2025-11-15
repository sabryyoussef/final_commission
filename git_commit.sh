#!/bin/bash

echo "Git Commit Script for Commission Module"
echo "======================================="

cd /workspaces/final_commission

# Initialize git if needed
if [ ! -d ".git" ]; then
    git init
    echo "Initialized git repository"
fi

# Check git status
echo "Current git status:"
git status

# Add all files
git add .

# Check what will be committed
echo "Files to be committed:"
git diff --cached --name-status

# Commit with comprehensive message
git commit -m "Implement commission filtering by paid/posted status

Features implemented:
- Modified commission sync to include ALL posted invoices (not just paid)
- Added three-tier filtering: paid, posted (unpaid), all
- Updated wizard default to 'posted' for forecast reporting
- Enhanced demo data with 9 comprehensive scenarios
- Updated all unit tests to reflect new functionality
- Added product commission rate validation
- Created testing and demo data scripts

Changes:
- commission_service.py: Removed payment_state filter, updated deletion logic
- wizard_commission_report.py: Changed default to 'posted', updated help text
- wizard_commission_report_views.xml: Updated UI descriptions
- demo_data.xml: Added comprehensive demo scenarios with commission lines
- All test files: Updated to test new filtering functionality
- product.py: Added commission rate validation constraints
- Created helper scripts for testing and demo data generation

This enables proper forecast vs actual commission reporting for business intelligence."

echo "Commit completed successfully!"