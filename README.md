# Financial Due Diligence (FDD) Automation Engine

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Pandas](https://img.shields.io/badge/Pandas-Data_Processing-150458.svg)](https://pandas.pydata.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-UI-FF4B4B.svg)](https://streamlit.io/)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57.svg)](https://www.sqlite.org/)
[![Plotly](https://img.shields.io/badge/Plotly-Visuals-3F4F75.svg)](https://plotly.com/)

A workflow product for financial due diligence that helps teams clean messy accounting data, run forensic accounting checks, and review flagged items inside a structured analyst workbench.

---

## Live Demo

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://fdd-automation-engine.streamlit.app/)

Sample files for a full workflow test are available in the repository’s **Releases** section under **Sample Data**.

### Method 1: Full workflow test
This is the best way to evaluate the product.

1. Open the live app.
2. Enter a new **Active Project Name**.
3. Enter the workspace password: `admin`
4. Upload the sample books and schedules.
5. Map the required columns.
6. Adjust runtime assumptions where needed.
7. Run the forensic sweep.
8. Review the flags dashboard, analyst ledger, and downloadable QoE report.

### Method 2: Instant preview mode
If you want to inspect the layout directly without running the full upload process:

- **Active Project Name:** `Project_Vedic`
- **Workspace Password:** `admin`

---

## What It Does

This engine is built around three linked functions:

### 1. Clean and normalize messy accounting data
The platform helps repair raw ERP-style extracts and standardize uploaded books into a more usable structure. It supports column mapping, text cleanup, date repair, and normalized data export for downstream analysis.

A cleaned **Normalized Databook** can be downloaded directly after repair and mapping.

### 2. Run forensic accounting tests
Once the books are structured, the engine runs a forensic sweep across the uploaded population. The logic is designed to identify accounting inconsistencies, suspicious transaction patterns, cut-off issues, provisioning gaps, hidden debt-style exposures, and other QoE-relevant risks.

The testing framework is also tied to a methodology wiki, so flagged items can be traced back to their test references and logic.

### 3. Provide an analyst workbench
The product does not stop at machine detection. Analysts can review flagged items, override machine amounts where needed, add rationale, attach evidence, and maintain a visible audit trail of judgment.

This makes the workflow more useful in practice, because diligence outputs often depend on documented review rather than fully automated conclusions.

---

## Core Workflow

The product follows a practical diligence flow:

1. Create or enter a deal workspace.
2. Upload the core books such as trial balance and general ledger.
3. Map uploaded columns into the engine’s required structure.
4. Adjust key runtime assumptions such as materiality, cut-off buffer, outlier sensitivity, capex floor, and ECL logic based on the case.
5. Upload the account mapping schedule.
6. Upload supporting books, directories, and registers.
7. Run the forensic sweep.
8. Review red, amber, and cleared items in the dashboard and analyst workbench.
9. Export the final QoE-style report.

---

## Key Features

### Deal-based workspace
Each project runs inside its own named workspace with a password gate and isolated data environment.

### Multi-book ingestion
The platform is designed to work with multiple books, not just the general ledger. This allows more realistic diligence-style checks across financial and operational support files.

### Runtime assumption controls
Users can adjust the logic of the engine while uploading and preparing data. This includes settings such as materiality, cut-off testing buffer, outlier sensitivity, capitalization thresholds, and expected credit loss assumptions.

This matters because forensic output should adapt to the engagement context rather than force one rigid rule-set on every company.

### Mapping-led standardization
A dedicated mapping layer helps translate client-specific account names into standardized analytical buckets.

### AI fallback prompt for account mapping
Where ledger naming is messy or the chart of accounts is unclear, the platform provides a practical fallback prompt that helps analysts speed up the account-mapping exercise. It is meant to support judgment, not replace it.

This is especially useful when dealing with legacy account names, vague ledger labels, or large-volume mapping exercises that would otherwise be slow to do manually.

### Normalized databook export
Users can repair and export a cleaner version of messy uploaded ledger data for downstream modeling or review.

### Forensic test library
The product runs a structured suite of accounting tests across the uploaded population and surfaces the output through dashboard references and a methodology wiki.

### Analyst ledger and override trail
Flagged items can be reviewed, modified, waived, or supported with uploaded evidence, while preserving machine output, analyst amount, variance, rationale, category, party reference, and timestamp.

### QoE-style output
The platform generates downloadable output designed to support a Quality of Earnings style review process, including summary math, categorized flags, and analyst workpapers.

---

## Architectural Design

The product uses a dual-vault structure to separate source data from analyst workpapers:

- **Vault A (`fdd_vault.db`)** stores raw uploaded books and ingestion-stage data.
- **Vault B (`fdd_workpapers.db`)** stores analyst review outputs, overrides, evidence references, and workpaper-style logs.

This separation helps preserve a cleaner distinction between client-provided inputs and analyst intervention.

---

## Books and Files Used

The workflow is designed for books commonly seen in diligence, including:

- General Ledger
- Trial Balance
- Profit and Loss
- Balance Sheet
- AR Aging
- AP Aging
- Payroll Register
- HRMS Master
- Lease Register
- Related Party Directory
- Bank Statement
- Bank Reconciliation
- Inventory Aging
- Vendor Master
- Other operational schedules and support files

---

## Technical Stack

- **Python**
- **Pandas**
- **Streamlit**
- **SQLite**
- **Plotly**

---

## Current Status

This is a working workflow product with:

- deal-based workspace setup,
- upload and mapping flows,
- runtime assumption controls,
- normalized databook export,
- forensic flag generation,
- analyst override and evidence logging,
- methodology wiki support,
- and downloadable QoE-style output.

It is best understood as a finance workflow product built around due diligence mechanics, not just a dashboard demo.

---

## Use Cases

Relevant use cases include:

- Financial Due Diligence
- Quality of Earnings support
- Transaction advisory workflows
- Accounting risk review
- Analyst productivity tooling
- Finance workflow automation

---

## Disclaimer

This repository is a portfolio and demonstration project. Any sample data used for testing, demo workspaces, or walkthroughs is synthetic and created for demonstration purposes only. No confidential client data is intended to be processed or exposed through the public demo.
