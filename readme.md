<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11%2B-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-Backend-green?logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/Frontend-HTML%2FCSS%2FJS-orange?logo=html5" alt="Frontend">
  <img src="https://img.shields.io/badge/Data-CSV-lightgrey?logo=file-csv" alt="CSV">
  <img src="https://img.shields.io/badge/Version-v1.0-brightgreen" alt="Version">
  <img src="https://img.shields.io/badge/License-MIT-lightblue" alt="License">
</p>

# 🧬 cPRArgentina – v1.0

**FastAPI-based calculator for cPRA estimation using HLA and ABO donor data – Autonomous City of Buenos Aires implementation.**

This is a **FastAPI-based** application that calculates the *calculated Panel Reactive Antibody (cPRA)* for a patient based on their list of unacceptable HLA antigens and ABO blood group.  
This version uses a **CSV file** containing donor HLA and ABO data as its source.

---

- **frontend/index.html** → basic web interface for testing the cPRA API.

---

## 🚀 Main Functionality

The `/calc_cpra` endpoint calculates the percentage of incompatible donors for a given set of HLA antigens and ABO group, returning the corresponding **cPRA** value.

Example request (`POST /calc_cpra`):

```json
{
  "antigenos": ["A2", "B44", "DR7"],
  "abo": "A"
}

---
## 🧮 ABO-adjusted cPRA model

The ABO-adjusted calculated Panel Reactive Antibody (cPRA) value is computed according to the methodology proposed by Gragert et al. (Am J Transplant, 2022).  
This approach integrates both HLA-incompatibility and the probability of ABO-incompatible donors within the donor pool.

The adjusted cPRA is calculated as:

**Formula:**  
`cPRA_ABOadj = cPRA_HLA + (1 - cPRA_HLA) × f_ABO-incompatible`

where:

- **cPRA<sub>HLA</sub>** is the fraction of donors with one or more unacceptable HLA antigens.  
- **f<sub>ABO-incompatible</sub>** is the summed phenotype frequency of donors that are ABO-incompatible with the candidate, calculated from the local donor dataset.

This implementation automatically derives ABO phenotype frequencies from the donor CSV file, providing a locally adjusted metric of immunologic compatibility.

---
## 👨‍💻 About

Developed and maintained by **Manuel Quirno Costa**  
Oxford 🇬🇧 · originally from Argentina 🇦🇷 · 2025

This project is part of an ongoing effort to adapt the calculated Panel Reactive Antibody (cPRA) model to local donor data using open-source tools.

If you find this useful, feel free to ⭐ star the repository or share feedback!

---
## ⚖️ License

This project is released under the **MIT License**, meaning it’s open for research, educational, and non-commercial use with proper attribution.

---
**Reference:**  
Gragert L, Kadatz M, Alcorn J, Stewart D, Chang D, Gill J, Liwski R, Gebel HM, Gill J, Lan JH.  
*ABO-adjusted calculated panel reactive antibody (cPRA): A unified metric for immunologic compatibility in kidney transplantation.*  
Am J Transplant. 2022;22(12):3093–3100. doi:[10.1111/ajt.17175](https://doi.org/10.1111/ajt.17175)

