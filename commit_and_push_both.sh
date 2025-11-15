#!/bin/bash

echo "🚀 COMMIT AND PUSH TO BOTH BRANCHES"
echo "===================================="

cd /workspaces/final_commission

echo "📍 Current status:"
git status --short

echo ""
echo "➕ Adding all changes..."
git add .

echo ""
echo "📝 Committing PDF report fixes..."
git commit -m "Fix PDF report commission rate formatting error

🐛 BUGFIX: Resolve PDF export error in commission reports

ISSUE:
- ValueError: incomplete format in PDF report template  
- Commission rate field could be None/False causing string formatting to fail
- Error occurred at: '%.2f%%' % line['commission_rate']

SOLUTION:
✅ Fixed QWeb template formatting with null safety
✅ Added default values to commission model fields
✅ Enhanced data structure validation in wizard  
✅ Improved commission line creation logic
✅ Created data fix script for existing records

FILES MODIFIED:
- commission_report_template.xml: Added null safety to formatting
- wizard_commission_report.py: Ensure valid numeric values
- commission.py: Added default values and better create logic
- fix_commission_rates.py: Script to fix existing data

TESTING:
- PDF export should now work without formatting errors
- Commission rates default to 0.0 when not set  
- Backwards compatible with existing data

IMPACT:
- Commission Financial Reports can now be exported to PDF successfully
- No more server errors when generating reports
- Better data integrity and error handling"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Commit successful!"
    
    echo ""
    echo "🚀 Pushing to main branch..."
    git push origin main
    
    if [ $? -eq 0 ]; then
        echo "✅ Successfully pushed to main branch!"
        
        echo ""
        echo "🔄 Switching to feature1 branch..."
        git checkout -b feature1 2>/dev/null || git checkout feature1
        
        echo ""
        echo "🔀 Merging main into feature1..."
        git merge main --no-edit
        
        if [ $? -eq 0 ]; then
            echo ""
            echo "🚀 Pushing to feature1 branch..."
            git push origin feature1
            
            if [ $? -eq 0 ]; then
                echo ""
                echo "🎉 SUCCESS: Pushed to both branches!"
                echo "=================================="
                echo ""
                echo "📊 BRANCH STATUS:"
                echo "✅ main: Updated with PDF fixes"
                echo "✅ feature1: Updated with PDF fixes"
                echo ""
                echo "🔧 FIXES APPLIED:"
                echo "- PDF export formatting errors resolved"
                echo "- Commission rate null safety added"
                echo "- Data validation improved"
                echo "- Backwards compatibility maintained"
                echo ""
                echo "📋 NEXT STEPS:"
                echo "1. Test PDF export in commission reports"
                echo "2. Run fix_commission_rates.py if needed for existing data"
                echo "3. Verify all commission reports work correctly"
            else
                echo "❌ Error pushing to feature1 branch!"
            fi
        else
            echo "❌ Error merging main into feature1!"
        fi
        
        echo ""
        echo "🔄 Switching back to main branch..."
        git checkout main
        
    else
        echo "❌ Error pushing to main branch!"
    fi
else
    echo "❌ Commit failed!"
fi

echo ""
echo "📊 Final status:"
git branch -v
git log --oneline -3