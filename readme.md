<p align="center"> <img src="https://img.shields.io/badge/Python-3.11%2B-blue?logo=python" alt="Python"> <img src="https://img.shields.io/badge/FastAPI-Backend-green?logo=fastapi" alt="FastAPI"> <img src="https://img.shields.io/badge/Frontend-HTML%2FCSS%2FJS-orange?logo=html5" alt="Frontend"> <img src="https://img.shields.io/badge/Data-SQLite-blueviolet?logo=sqlite" alt="SQLite"> <img src="https://img.shields.io/badge/Version-v1.0-brightgreen" alt="Version"> <img src="https://img.shields.io/badge/License-MIT-lightblue" alt="License"> </p>
🧬 cPRArgentina – v1.0

ABO-adjusted cPRA calculator based on Argentine donor data.

This project implements a FastAPI-based application for estimating the calculated Panel Reactive Antibody (cPRA) of a transplant candidate using:

Empirical HLA donor incompatibility

ABO-adjusted probability modeling

A local Argentine donor database (SQLite)

The goal is to provide a transparent and locally adapted immunologic compatibility metric.

🚀 Main Functionality

The /calc_cpra endpoint calculates the percentage of immunologically incompatible donors for a given set of unacceptable HLA antigens and ABO blood group.

Two calculation modes are available:

Probabilistic (freq) → ABO-adjusted model assuming independence between HLA and ABO.

Empirical (filter) → Direct filtering of incompatible donors in the dataset.

Example request:

{
"antigenos": ["A2", "B44", "DR7"],
"abo": "A",
"mode": "freq"
}

Example response:

{
"cPRA": 76.2,
"N_donors": 171,
"mode_used": "FREQ",
"last_update": "2026-02-22 18:12:03"
}

🧮 Methodology

The ABO-adjusted cPRA follows the approach described by:

Gragert et al. (Am J Transplant, 2022)

Formula:

cPRA_ABOadj = cPRA_HLA + (1 − cPRA_HLA) × f_ABO-incompatible

Where:

cPRA_HLA is calculated empirically as the fraction of donors carrying at least one unacceptable HLA antigen.

f_ABO-incompatible is the summed phenotype frequency of ABO-incompatible donors derived dynamically from the local donor database.

The empirical (filter) mode directly computes:

(# donors incompatible by HLA, ABO, or both) / total donors

This approach is conceptually aligned with previously described simplified donor-pool–based cPRA calculations (Chan et al., 2017).

This dual implementation allows methodological comparison and transparency.

📊 Data Source

Donor data are stored in a local SQLite database.

By default, the application uses cpra_demo.db (synthetic demo dataset).

A real dataset can be loaded into cpra.db.

ABO phenotype frequencies are calculated dynamically from the dataset.

Total donor count and last update timestamp are exposed via /dataset_info.

The model therefore reflects the effective donor pool rather than general population estimates.

⚙️ Running Locally

Install dependencies (recommended inside a virtual environment):

pip install -r requirements.txt

Run the server:

uvicorn main:app --reload

Open in browser:

http://127.0.0.1:8000

Interactive API documentation:

http://127.0.0.1:8000/docs

🧪 Demo Database

A small synthetic demo database can be generated for testing purposes:

python init_demo_db.py

By default, the application uses cpra_demo.db.

To use a real database instead:

set CPRA_DB=cpra.db
uvicorn main:app --reload

⚠️ Disclaimer

Research Use Only.

This tool is intended for research, methodological validation, and educational purposes.
It is not intended for direct clinical decision-making without independent verification.

👨‍💻 About

Developed by Manuel Quirno Costa
Originally from Argentina 🇦🇷 · 2026

This project aims to adapt the cPRA framework to locally derived donor data using open-source tools.

📚 References

Gragert L, Kadatz M, Alcorn J, Stewart D, Chang D, Gill J, Liwski R, Gebel HM, Gill J, Lan JH.
ABO-adjusted calculated panel reactive antibody (cPRA): A unified metric for immunologic compatibility in kidney transplantation.
Am J Transplant. 2022;22(12):3093–3100.
https://doi.org/10.1111/ajt.17175

Chan YP, Wong MWK, Tang LWM, Guo M, Yang W, Ip P, Li PKT, Leung CB, Chau KF, Lam JCK, Yeung NKM, Kwok JSY.
A simplified method of calculating cPRA for kidney allocation application in Hong Kong: a retrospective study.
Transpl Int. 2017 Dec;30(12):1234–1242.
doi: 10.1111/tri.13015
PMID: 28777478
https://pubmed.ncbi.nlm.nih.gov/28777478/