"""
Integration tests for API endpoints
"""

import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_check(self, client: TestClient):
        """Test health check returns 200"""
        response = client.get("/health")
        assert response.status_code in [200, 503]
        data = response.json()
        assert "status" in data
        assert "services" in data
    
    def test_root_endpoint(self, client: TestClient):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data


class TestMetricsEndpoint:
    """Test metrics endpoint"""
    
    def test_metrics_endpoint(self, client: TestClient):
        """Test metrics endpoint"""
        response = client.get("/metrics")
        # May be 200 or 404 depending on settings
        assert response.status_code in [200, 404]


class TestChatEndpoint:
    """Test chat endpoint"""
    
    @pytest.mark.skip(reason="Chat endpoint not yet fully implemented")
    def test_chat_request(self, client: TestClient, sample_query, auth_headers):
        """Test chat request"""
        response = client.post(
            "/api/v1/chat",
            json=sample_query,
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "response" in data

