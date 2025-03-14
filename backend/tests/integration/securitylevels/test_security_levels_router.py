from fastapi.testclient import TestClient
from intric.tenants.tenant import TenantInDB

def test_create_security_level(test_client: TestClient, test_tenant: TenantInDB):

  # Create a new security level
  response = test_client.post(
    "/api/v1/security-levels",
    json={
      "name": "test",
      "description": "test",
      "value": 1,
      "tenant_id": f"{test_tenant.id}"
    })
  assert response.status_code == 200
