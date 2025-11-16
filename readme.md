# 🧬 cPRA 3.0 – CSV Version

**cPRA 3.0** is a **FastAPI-based** application that calculates the *calculated Panel Reactive Antibody (cPRA)* for a patient based on their list of unacceptable HLA antigens and ABO blood group.  
This version uses a **CSV file** containing donor HLA and ABO data as its source (no MySQL database required).

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
