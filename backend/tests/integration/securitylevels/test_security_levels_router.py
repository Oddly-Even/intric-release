from fastapi.testclient import TestClient
from intric.tenants.tenant import TenantInDB
from sqlalchemy import text

async def test_list_all_users(test_client, test_user, test_tenant, test_jwt_token: str):
  """Test listing all security levels via the API."""

  response = await test_client.get("/api/v1/security-levels", headers={"Authorization": f"Bearer {test_jwt_token}"})
  assert response.status_code == 200
