# 🔎 Financial Due Diligence (FDD) Automation Engine

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Pandas](https://img.shields.io/badge/Pandas-Data_Processing-150458.svg)](https://pandas.pydata.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-UI-FF4B4B.svg)](https://streamlit.io/)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57.svg)](https://www.sqlite.org/)

**A high-performance algorithmic workspace engineered to eliminate manual sampling, sanitize messy ERP extractions, and accelerate the Quality of Earnings (QoE) process for M&A transactions.**

---

## 🎥 Demonstration

> **Note to Reviewers:** Due to the strict confidentiality requirements of M&A transaction advisory, this application is not hosted on a live public server. 
> 
> 🔗 **[Click here to watch a 60-second video demonstration of the FDD Engine in action using dummy dataset simulations.]** *(Link to your Loom video or YouTube unlisted video here)*

### 🔐 Live Demonstration Access

>This engine is built with a Dual-Vault Architecture to simulate secure M&A deal rooms. To review the dashboard and execution deck, please use the following demo credentials:
>
>* **Active Project Name:** `Project_Vedic`
>* **Workspace Password:** `admin`

---

## 💡 The Business Problem
In standard transaction advisory, the most expensive hours of the due diligence process are spent manually cleaning fractured General Ledgers, handling missing data across millions of rows, and index-matching across operational subledgers. This manual bottleneck limits the time analysts can spend on actual commercial risk assessment.

This engine automates the mechanical 80% of the FDD process. It instantly structures disorganized ledger outputs, executes rules-based variance screens, and enforces an immutable audit trail for partner review.

---

## 🏗️ Architectural Highlight: The Dual-Vault System
To solve the cardinal risk of audit workpapers being accidentally overwritten or contaminated by raw client file re-uploads, this application utilizes a strictly segregated **Dual-Vault Architecture**:

*   **Vault A (`fdd_vault.db`):** An isolated database for raw, client-provided ERP data and initial file ingestion.
*   **Vault B (`fdd_workpapers.db`):** An immutable, analyst-driven logging database that strictly houses the QoE bridges, manual pro-forma adjustments, and attached evidentiary files (.pdf/.xlsx). 

---

## 🚀 Core Engine Capabilities

### 1. Intelligent Data Sanitization (Pandas Core)
Raw client ledgers are rarely clean. The engine utilizes advanced Pandas workflows to act as a standalone data standardization tool. It automatically drops corrupted rows, fixes broken accounting date formats, normalizes text strings, and exports a unified "Normalized Databook" ready for deal team financial models.

### 2. The Vectorized Forensic Sweep
Shift seamlessly between **Ind AS, US GAAP, and IFRS**. The engine dynamically executes up to 25 specialized forensic protocols, instantly scanning 100% of the ledger population for:
*   Revenue cut-off bleeds and year-end window dressing.
*   Phantom vendors and related-party transaction clustering.
*   Expected Credit Loss (ECL) shortfalls.
*   Unrecorded shadow debt and working capital anomalies.

### 3. Multi-Book Triangulation & AI Mapping
Fraud and execution gaps rarely live in the General Ledger alone. The engine cross-references GL transactions against operational subledgers (e.g., Warehouse Dispatch Logs, HRMS Masters, Bank Statements). For highly unstructured legacy account names, an integrated AI fallback routes vague cost centers into strict QoE categories.

### 4. Partner-Ready Analyst Workbench
The machine does not replace the analyst; it accelerates them. The UI provides a dedicated workbench to explicitly waive pending risk flags, log manual discoveries, and attach mandatory documentation for any adjustments. Outputs directly to a multi-sheet, partner-ready QoE Excel report.

---

## 🛠️ Technical Stack
*   **Backend & Data Processing:** Python, Pandas (Heavy vectorized data manipulation, dataframe merging, and missing data handling)
*   **Frontend UI:** Streamlit (Custom hybrid multi-page architecture)
*   **Database:** SQLite (Segregated Dual-Vault deployment)
*   **Core Logic:** Regex string tokenization, financial variance mapping, exception-based routing.

---

## ⚠️ Disclaimer
*This repository is a portfolio piece designed for educational and professional demonstration purposes. All data utilized in the demonstration video and sample files are synthetically generated dummy datasets. No proprietary, confidential, or live transaction data is processed or stored in this codebase.*
