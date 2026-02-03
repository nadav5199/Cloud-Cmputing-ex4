"""
Assignment 4 - Pytest tests for Pet Store CI/CD pipeline.
Tests the pet-store and pet-order services as specified in the assignment.
"""

import pytest
import requests
import time

# Service URLs
STORE1_URL = "http://localhost:5001"
STORE2_URL = "http://localhost:5002"
ORDER_URL = "http://localhost:5003"

# Pet Type payloads (as specified in assignment)
PET_TYPE1 = {"type": "Golden Retriever"}
PET_TYPE2 = {"type": "Australian Shepherd"}
PET_TYPE3 = {"type": "Abyssinian"}
PET_TYPE4 = {"type": "bulldog"}

# Expected values after Ninja API enrichment
PET_TYPE1_VAL = {
    "type": "Golden Retriever",
    "family": "Canidae",
    "genus": "Canis",
}

PET_TYPE2_VAL = {
    "type": "Australian Shepherd",
    "family": "Canidae",
    "genus": "Canis",
}

PET_TYPE3_VAL = {
    "type": "Abyssinian",
    "family": "Felidae",
    "genus": "Felis",
}

PET_TYPE4_VAL = {
    "type": "bulldog",
    "family": "Canidae",
    "genus": "Canis",
}

# Pet payloads (as specified in assignment)
PET1_TYPE1 = {"name": "Lander", "birthdate": "14-05-2020"}
PET2_TYPE1 = {"name": "Lanky"}
PET3_TYPE1 = {"name": "Shelly", "birthdate": "07-07-2019"}
PET4_TYPE2 = {"name": "Felicity", "birthdate": "27-11-2011"}
PET5_TYPE3 = {"name": "Muscles"}
PET6_TYPE3 = {"name": "Junior"}
PET7_TYPE4 = {"name": "Lazy", "birthdate": "07-08-2018"}
PET8_TYPE4 = {"name": "Lemon", "birthdate": "27-03-2020"}

# Store IDs returned from POST requests
store1_ids = {}  # id_1, id_2, id_3
store2_ids = {}  # id_4, id_5, id_6


@pytest.fixture(scope="module", autouse=True)
def wait_for_services():
    """Wait for all services to be ready before running tests."""
    max_retries = 60
    for i in range(max_retries):
        try:
            r1 = requests.get(f"{STORE1_URL}/", timeout=2)
            r2 = requests.get(f"{STORE2_URL}/", timeout=2)
            if r1.status_code == 200 and r2.status_code == 200:
                print(f"Services ready after {i+1} attempts")
                time.sleep(2)  # Extra wait for stability
                return
        except requests.exceptions.RequestException:
            pass
        time.sleep(1)
    pytest.fail("Services did not become ready in time")


class TestPostPetTypesToStore1:
    """
    Tests 1-2: POST 3 pet-types to pet store #1.
    PET_TYPE1, PET_TYPE2, PET_TYPE3
    """

    def test_post_pet_type1_to_store1(self):
        """POST PET_TYPE1 (Golden Retriever) to store #1."""
        response = requests.post(
            f"{STORE1_URL}/pet-types",
            json=PET_TYPE1,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        assert response.status_code == 201, f"Expected 201, got {response.status_code}"
        data = response.json()
        assert "id" in data
        assert data["family"] == PET_TYPE1_VAL["family"]
        assert data["genus"] == PET_TYPE1_VAL["genus"]
        store1_ids["id_1"] = data["id"]

    def test_post_pet_type2_to_store1(self):
        """POST PET_TYPE2 (Australian Shepherd) to store #1."""
        response = requests.post(
            f"{STORE1_URL}/pet-types",
            json=PET_TYPE2,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        assert response.status_code == 201, f"Expected 201, got {response.status_code}"
        data = response.json()
        assert "id" in data
        assert data["family"] == PET_TYPE2_VAL["family"]
        assert data["genus"] == PET_TYPE2_VAL["genus"]
        store1_ids["id_2"] = data["id"]

    def test_post_pet_type3_to_store1(self):
        """POST PET_TYPE3 (Abyssinian) to store #1."""
        response = requests.post(
            f"{STORE1_URL}/pet-types",
            json=PET_TYPE3,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        assert response.status_code == 201, f"Expected 201, got {response.status_code}"
        data = response.json()
        assert "id" in data
        assert data["family"] == PET_TYPE3_VAL["family"]
        assert data["genus"] == PET_TYPE3_VAL["genus"]
        store1_ids["id_3"] = data["id"]

    def test_store1_ids_unique(self):
        """Verify all IDs returned from store #1 are unique."""
        ids = list(store1_ids.values())
        assert len(ids) == len(set(ids)), "IDs from store #1 are not unique"


class TestPostPetTypesToStore2:
    """
    Test 2: POST 3 pet-types to pet store #2.
    PET_TYPE1, PET_TYPE2, PET_TYPE4
    """

    def test_post_pet_type1_to_store2(self):
        """POST PET_TYPE1 (Golden Retriever) to store #2."""
        response = requests.post(
            f"{STORE2_URL}/pet-types",
            json=PET_TYPE1,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        assert response.status_code == 201, f"Expected 201, got {response.status_code}"
        data = response.json()
        assert "id" in data
        assert data["family"] == PET_TYPE1_VAL["family"]
        assert data["genus"] == PET_TYPE1_VAL["genus"]
        store2_ids["id_4"] = data["id"]

    def test_post_pet_type2_to_store2(self):
        """POST PET_TYPE2 (Australian Shepherd) to store #2."""
        response = requests.post(
            f"{STORE2_URL}/pet-types",
            json=PET_TYPE2,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        assert response.status_code == 201, f"Expected 201, got {response.status_code}"
        data = response.json()
        assert "id" in data
        assert data["family"] == PET_TYPE2_VAL["family"]
        assert data["genus"] == PET_TYPE2_VAL["genus"]
        store2_ids["id_5"] = data["id"]

    def test_post_pet_type4_to_store2(self):
        """POST PET_TYPE4 (bulldog) to store #2."""
        response = requests.post(
            f"{STORE2_URL}/pet-types",
            json=PET_TYPE4,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        assert response.status_code == 201, f"Expected 201, got {response.status_code}"
        data = response.json()
        assert "id" in data
        assert data["family"] == PET_TYPE4_VAL["family"]
        assert data["genus"] == PET_TYPE4_VAL["genus"]
        store2_ids["id_6"] = data["id"]

    def test_store2_ids_unique(self):
        """Verify all IDs returned from store #2 are unique."""
        ids = list(store2_ids.values())
        assert len(ids) == len(set(ids)), "IDs from store #2 are not unique"


class TestPostPetsToStore1:
    """
    Tests 3-4: POST pets to pet-types in store #1.
    - POST PET1_TYPE1, PET2_TYPE1 to id_1 (Golden Retriever)
    - POST PET5_TYPE3, PET6_TYPE3 to id_3 (Abyssinian)
    """

    def test_post_pet1_type1_to_store1(self):
        """POST PET1_TYPE1 (Lander) to id_1 in store #1."""
        assert "id_1" in store1_ids, "id_1 not available"
        response = requests.post(
            f"{STORE1_URL}/pet-types/{store1_ids['id_1']}/pets",
            json=PET1_TYPE1,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        assert response.status_code == 201, f"Expected 201, got {response.status_code}"

    def test_post_pet2_type1_to_store1(self):
        """POST PET2_TYPE1 (Lanky) to id_1 in store #1."""
        assert "id_1" in store1_ids, "id_1 not available"
        response = requests.post(
            f"{STORE1_URL}/pet-types/{store1_ids['id_1']}/pets",
            json=PET2_TYPE1,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        assert response.status_code == 201, f"Expected 201, got {response.status_code}"

    def test_post_pet5_type3_to_store1(self):
        """POST PET5_TYPE3 (Muscles) to id_3 in store #1."""
        assert "id_3" in store1_ids, "id_3 not available"
        response = requests.post(
            f"{STORE1_URL}/pet-types/{store1_ids['id_3']}/pets",
            json=PET5_TYPE3,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        assert response.status_code == 201, f"Expected 201, got {response.status_code}"

    def test_post_pet6_type3_to_store1(self):
        """POST PET6_TYPE3 (Junior) to id_3 in store #1."""
        assert "id_3" in store1_ids, "id_3 not available"
        response = requests.post(
            f"{STORE1_URL}/pet-types/{store1_ids['id_3']}/pets",
            json=PET6_TYPE3,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        assert response.status_code == 201, f"Expected 201, got {response.status_code}"


class TestPostPetsToStore2:
    """
    Tests 5-7: POST pets to pet-types in store #2.
    - POST PET3_TYPE1 to id_4 (Golden Retriever)
    - POST PET4_TYPE2 to id_5 (Australian Shepherd)
    - POST PET7_TYPE4, PET8_TYPE4 to id_6 (bulldog)
    """

    def test_post_pet3_type1_to_store2(self):
        """POST PET3_TYPE1 (Shelly) to id_4 in store #2."""
        assert "id_4" in store2_ids, "id_4 not available"
        response = requests.post(
            f"{STORE2_URL}/pet-types/{store2_ids['id_4']}/pets",
            json=PET3_TYPE1,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        assert response.status_code == 201, f"Expected 201, got {response.status_code}"

    def test_post_pet4_type2_to_store2(self):
        """POST PET4_TYPE2 (Felicity) to id_5 in store #2."""
        assert "id_5" in store2_ids, "id_5 not available"
        response = requests.post(
            f"{STORE2_URL}/pet-types/{store2_ids['id_5']}/pets",
            json=PET4_TYPE2,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        assert response.status_code == 201, f"Expected 201, got {response.status_code}"

    def test_post_pet7_type4_to_store2(self):
        """POST PET7_TYPE4 (Lazy) to id_6 in store #2."""
        assert "id_6" in store2_ids, "id_6 not available"
        response = requests.post(
            f"{STORE2_URL}/pet-types/{store2_ids['id_6']}/pets",
            json=PET7_TYPE4,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        assert response.status_code == 201, f"Expected 201, got {response.status_code}"

    def test_post_pet8_type4_to_store2(self):
        """POST PET8_TYPE4 (Lemon) to id_6 in store #2."""
        assert "id_6" in store2_ids, "id_6 not available"
        response = requests.post(
            f"{STORE2_URL}/pet-types/{store2_ids['id_6']}/pets",
            json=PET8_TYPE4,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        assert response.status_code == 201, f"Expected 201, got {response.status_code}"


class TestGetRequests:
    """
    Tests 8-9: GET requests to verify data.
    """

    def test_get_pet_type2_from_store1(self):
        """
        Test 8: GET /pet-types/{id_2} from store #1.
        Verify JSON matches PET_TYPE2_VAL fields.
        """
        assert "id_2" in store1_ids, "id_2 not available"
        response = requests.get(
            f"{STORE1_URL}/pet-types/{store1_ids['id_2']}",
            timeout=10
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data["family"] == PET_TYPE2_VAL["family"]
        assert data["genus"] == PET_TYPE2_VAL["genus"]

    def test_get_pets_of_type4_from_store2(self):
        """
        Test 9: GET /pet-types/{id_6}/pets from store #2.
        Verify returned array contains PET7_TYPE4 and PET8_TYPE4.
        """
        assert "id_6" in store2_ids, "id_6 not available"
        response = requests.get(
            f"{STORE2_URL}/pet-types/{store2_ids['id_6']}/pets",
            timeout=10
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert isinstance(data, list), "Expected list of pets"

        # Check that both pets are present
        pet_names = [pet["name"] for pet in data]
        assert PET7_TYPE4["name"] in pet_names, f"Expected {PET7_TYPE4['name']} in pets"
        assert PET8_TYPE4["name"] in pet_names, f"Expected {PET8_TYPE4['name']} in pets"
