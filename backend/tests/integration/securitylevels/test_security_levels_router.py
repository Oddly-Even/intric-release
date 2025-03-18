from fastapi.testclient import TestClient
from intric.tenants.tenant import TenantInDB
from sqlalchemy import text

async def test_list_all_users(db_session, test_client, test_user, test_tenant, container, test_jwt_token: str):
  """Test listing all security levels via the API."""
  async with db_session.begin():
    security_level_service = container.security_level_service()
    sec_level = await security_level_service.create_security_level(name="Low Security", description="Low Security", value=1)
    await db_session.commit()

  response = await test_client.get("/api/v1/security-levels", headers={"Authorization": f"Bearer {test_jwt_token}"})
  assert response.status_code == 200

  data = response.json()
  print("DATA", data)
  assert len(data) == 1
