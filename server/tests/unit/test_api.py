"""API 单元测试示例"""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root():
    """测试根路径"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_health_check():
    """测试健康检查"""
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_create_profile():
    """测试创建用户画像"""
    profile_data = {
        "user_id": "test_user",
        "grade": 5,
        "interests": ["足球", "科学实验"],
    }
    response = client.post("/profiles", json=profile_data)
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["user_id"] == "test_user"


def test_get_profile():
    """测试获取用户画像"""
    # 先创建
    profile_data = {
        "user_id": "test_user_2",
        "grade": 3,
        "interests": ["音乐"],
    }
    client.post("/profiles", json=profile_data)
    
    # 再获取
    response = client.get("/profiles/test_user_2")
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["grade"] == 3


def test_get_nonexistent_profile():
    """测试获取不存在的用户画像"""
    response = client.get("/profiles/nonexistent")
    assert response.status_code == 404
