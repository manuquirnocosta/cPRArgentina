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
