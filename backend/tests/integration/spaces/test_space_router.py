from tests.integration.conftest import user_token

async def test_create_space(test_client, container):
  """Test creating a space via the API."""

  response = await test_client.post("/api/v1/spaces", headers={"Authorization": f"Bearer {user_token(container)}"}, json={
    "name": "Test Space",
  })
  assert response.status_code == 201
  assert response.json()["name"] == "Test Space"

async def test_list_spaces(test_client, container):
  """Test listing all spaces via the API."""
  async with container.session().begin():
    await container.space_service().create_space(
      name="Test Space",
    )

  response = await test_client.get("/api/v1/spaces", headers={"Authorization": f"Bearer {user_token(container)}"})
  assert response.status_code == 200
  assert len(response.json()["items"]) == 1
  assert response.json()["items"][0]["name"] == "Test Space"

async def test_get_space(test_client, container):
  """Test getting a space via the API."""

  async with container.session().begin():
    space = await container.space_service().create_space(
      name="Test Space",
    )

  response = await test_client.get(f"/api/v1/spaces/{space.id}", headers={"Authorization": f"Bearer {user_token(container)}"})
  assert response.status_code == 200
  assert response.json()["name"] == "Test Space"
