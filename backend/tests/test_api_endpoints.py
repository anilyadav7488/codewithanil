import pytest

def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "model_name" in data

def test_model_info_endpoint(client):
    response = client.get("/api/model/info")
    assert response.status_code == 200
    data = response.json()
    assert "RoBERTa" in data["architecture"]
    assert "decision_thresholds" in data
    assert "known_limitations" in data
    assert len(data["known_limitations"]) > 0

def test_analyze_prompt_endpoint(client):
    payload = {
        "prompt": "You are a senior systems engineer. Write a high-performance Python script to parse a 5GB log file. Format the output in Markdown."
    }
    response = client.post("/api/analyze/prompt", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["overall_score"] >= 60
    assert "metrics" in data
    assert "clarity" in data["metrics"]
    assert "improved_prompt" in data
    assert len(data["strengths"]) > 0

def test_analyze_text_validation_empty(client):
    response = client.post("/api/analyze/text", json={"text": ""})
    assert response.status_code in [400, 422]

def test_analyze_text_validation_too_short(client):
    response = client.post("/api/analyze/text", json={"text": "Short prompt here."})
    assert response.status_code == 400
    data = response.json()
    assert "Minimum 15 words required" in data["detail"]

def test_auth_registration_and_login_flow(client):
    email = "testuser@codewithanil.com"
    password = "StrongPassword123!"
    
    # 1. Register
    reg_response = client.post("/api/auth/register", json={
        "name": "Anil Tester",
        "email": email,
        "password": password
    })
    assert reg_response.status_code == 201
    reg_data = reg_response.json()
    assert "access_token" in reg_data
    assert reg_data["user"]["email"] == email

    # 2. Login
    login_response = client.post("/api/auth/login", json={
        "email": email,
        "password": password
    })
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # 3. Access Protected Route /auth/me
    headers = {"Authorization": f"Bearer {token}"}
    me_response = client.get("/api/auth/me", headers=headers)
    assert me_response.status_code == 200
    assert me_response.json()["name"] == "Anil Tester"

    # 4. Access user stats
    stats_response = client.get("/api/analysis/stats", headers=headers)
    assert stats_response.status_code == 200
    stats_data = stats_response.json()
    assert "total_analyses" in stats_data
