# Sales Commission by Product Invoice — User Guide

## Overview
This module calculates sales commissions based on paid customer invoices and credit notes. Commission rates are defined per product on the product template, and resulting commission lines are available in a dedicated reporting menu under Sales.

---

## Prerequisites
- Install and upgrade the module `sales_commission_product`.
- Ensure your user belongs to the `Sales Commission Manager` group to access reporting and configuration.
- Confirm the scheduled action **Sales Commission Sync** is active (runs nightly). Managers can trigger it manually from **Settings → Technical → Automation → Scheduled Actions**.

---

## Configure Product Commission Rates
1. Go to **Sales → Products → Products**.
2. Open a product and switch to the **Sales** tab.
3. Set the **Commission Rate (%)** field (e.g., enter `5.0` for 5%).
4. Save the product. The rate applies to all variants derived from this template.

---

## How Commissions Are Generated
The system creates `Sales Commission Line` records from invoice lines that meet these conditions:
- **Customer Invoice** (`Posted`, `Paid`): commission is positive.
- **Customer Credit Note** (`Posted`): commission is negative (deducts earnings).
- Products without a commission rate are ignored.

The scheduled action processes new posted lines automatically. To run it manually, users with manager rights can:
1. Go to **Settings → Technical → Automation → Scheduled Actions**.
2. Open **Sales Commission Sync**.
3. Click **Run Manually**.

---

## Reviewing Commission Reports
Navigate to **Sales → Reporting → Commission Report**.

### Views
- **Pivot (default)**: Aggregates commissions by salesperson (rows) and month (columns). Measures include commission amount and line subtotal.
- **Tree**: Lists detailed lines with invoice date, salesperson, invoice, product, subtotal, rate, and commission amount.
- **Graph**: Bar chart comparing commission amounts by salesperson.

### Filters & Group By
- Default filter: **This Month**.
- Use the search panel to filter by salesperson, invoice, product, or company (multi-company only).
- Group by options: salesperson, product, invoice month.

---

## Security & Access
- **Sales Commission Manager** group: full access to commission menu, data, and manual sync.
- Regular salespeople (optional) can view commission lines restricted to their own salesperson record via record rules.
- To grant access to the report:
  1. Go to **Settings → Users & Companies → Users**.
  2. Open the user record (e.g., your salesperson).
  3. Under the **Sales** section of Access Rights, activate **Sales Commission Manager**.
  4. Save the user and ask them to refresh their browser session. The **Sales → Reporting → Commission Report** menu will become visible.

---

## Troubleshooting
- **No commission lines appear**: verify invoices are posted and fully paid, products have a non-zero commission rate, and the scheduled action has run.
- **Credit note not deducting**: ensure the return is posted as a customer credit note (`out_refund`).
- **Access denied**: confirm the user’s group assignments (manager vs salesperson).
- **Cron not running**: check that **Sales Commission Sync** is active and monitor logs for errors.

---

## Optional Enhancements
- Seed demo data with sample invoices to showcase the report.
- Add automated tests for the commission computation service to guard against regressions.

