import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from main import app


def test_cpra_valido():
    with TestClient(app) as client:
        response = client.post(
            "/calc_cpra",
            json={
                "antigenos": ["A2"],
                "abo": "A"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "cPRA" in data
        assert isinstance(data["cPRA"], float)


def test_cpra_invalido():
    with TestClient(app) as client:
        response = client.post(
            "/calc_cpra",
            json={
                "antigenos": ["BANANA"],
                "abo": "A"
            }
        )

        assert response.status_code == 400

def test_cpra_entre_0_y_100():
    with TestClient(app) as client:
        response = client.post(
            "/calc_cpra",
            json={
                "antigenos": ["A2"],
                "abo": "A"
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert 0 <= data["cPRA"] <= 100


def test_agregar_antigeno_no_disminuye_cpra():
    with TestClient(app) as client:
        # cPRA con un antígeno
        r1 = client.post(
            "/calc_cpra",
            json={
                "antigenos": ["A2"],
                "abo": "A"
            }
        )

        # cPRA con dos antígenos
        r2 = client.post(
            "/calc_cpra",
            json={
                "antigenos": ["A2", "B44"],
                "abo": "A"
            }
        )

        assert r1.status_code == 200
        assert r2.status_code == 200

        cpra1 = r1.json()["cPRA"]
        cpra2 = r2.json()["cPRA"]

        # Agregar antígenos no debería bajar el cPRA
        assert cpra2 >= cpra1
