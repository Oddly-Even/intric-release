from tests.integration.conftest import user_token

async def test_list_security_levels(test_client, container):
  """Test listing all security levels via the API."""

  async with container.session().begin():
    await container.security_level_service().create_security_level(
      name="Test Security Level",
      description="Test Description",
      value=1,
    )

  response = await test_client.get("/api/v1/security-levels", headers={"Authorization": f"Bearer {user_token(container)}"})
  assert response.status_code == 200
  assert len(response.json()) == 1
  assert response.json()[0]["name"] == "Test Security Level"

async def test_create_security_level(test_client, container):
  """Test creating a new security level via the API."""

  response = await test_client.post("/api/v1/security-levels", headers={"Authorization": f"Bearer {user_token(container)}"}, json={
    "name": "Test Security Level",
    "description": "Test Description",
    "value": 1,
  })
  assert response.status_code == 201
  assert response.json()["name"] == "Test Security Level"
  assert response.json()["description"] == "Test Description"
  assert response.json()["value"] == 1

async def test_get_security_level(test_client, container):
  """Test getting a security level by ID via the API."""
  async with container.session().begin():
    security_level = await container.security_level_service().create_security_level(
      name="Test Security Level",
      description="Test Description",
      value=1,
    )

  response = await test_client.get(f"/api/v1/security-levels/{security_level.id}", headers={"Authorization": f"Bearer {user_token(container)}"})
  assert response.status_code == 200
  assert response.json()["name"] == "Test Security Level"

async def test_update_security_level(test_client, container):
  """Test updating a security level via the API."""
  async with container.session().begin():
    security_level = await container.security_level_service().create_security_level(
      name="Test Security Level",
      description="Test Description",
      value=1,
    )

  response = await test_client.patch(f"/api/v1/security-levels/{security_level.id}", headers={"Authorization": f"Bearer {user_token(container)}"}, json={
    "name": "Updated Security Level",
    "description": "Updated Description",
    "value": 2,
  })
  assert response.status_code == 200
  assert response.json()["name"] == "Updated Security Level"
  assert response.json()["description"] == "Updated Description"
  assert response.json()["value"] == 2
