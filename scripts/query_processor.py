#!/usr/bin/env python3
"""
Query processor for Assignment 4.
Reads query.txt and executes queries/purchases against pet-store services.
Outputs results to response.txt.

Query format: "query: <pet-store-num>,<field>=<value>;"
Purchase format: "purchase: <JSON-purchase>;"
"""

import requests
import json
import time
import sys

# Service URLs
STORE1_URL = "http://localhost:5001"
STORE2_URL = "http://localhost:5002"
ORDER_URL = "http://localhost:5003"

# Pet Type payloads (same as test file)
PET_TYPE1 = {"type": "Golden Retriever"}
PET_TYPE2 = {"type": "Australian Shepherd"}
PET_TYPE3 = {"type": "Abyssinian"}
PET_TYPE4 = {"type": "bulldog"}

# Pet payloads (same as test file)
PET1_TYPE1 = {"name": "Lander", "birthdate": "14-05-2020"}
PET2_TYPE1 = {"name": "Lanky"}
PET3_TYPE1 = {"name": "Shelly", "birthdate": "07-07-2019"}
PET4_TYPE2 = {"name": "Felicity", "birthdate": "27-11-2011"}
PET5_TYPE3 = {"name": "Muscles"}
PET6_TYPE3 = {"name": "Junior"}
PET7_TYPE4 = {"name": "Lazy", "birthdate": "07-08-2018"}
PET8_TYPE4 = {"name": "Lemon", "birthdate": "27-03-2020"}


def wait_for_services(max_retries=60):
    """Wait for services to be ready."""
    print("Waiting for services to be ready...")
    for i in range(max_retries):
        try:
            r1 = requests.get(f"{STORE1_URL}/", timeout=2)
            r2 = requests.get(f"{STORE2_URL}/", timeout=2)
            if r1.status_code == 200 and r2.status_code == 200:
                print(f"Services ready after {i+1} attempts")
                time.sleep(2)
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(1)
    print("Services did not become ready in time!")
    return False


def populate_data():
    """
    Populate stores with test data.
    Same POST requests as pytest steps 1-7.
    Returns dict of IDs: {id_1, id_2, id_3, id_4, id_5, id_6}
    """
    print("Populating data...")
    ids = {}

    # Step 1: POST 3 pet-types to store #1
    print("  POSTing pet types to store #1...")
    for name, pet_type in [("id_1", PET_TYPE1), ("id_2", PET_TYPE2), ("id_3", PET_TYPE3)]:
        try:
            r = requests.post(
                f"{STORE1_URL}/pet-types",
                json=pet_type,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            if r.status_code == 201:
                ids[name] = r.json()["id"]
                print(f"    {name}: {ids[name]} ({pet_type['type']})")
            else:
                print(f"    Failed to create {pet_type['type']}: {r.status_code}")
        except Exception as e:
            print(f"    Error creating {pet_type['type']}: {e}")

    # Step 2: POST 3 pet-types to store #2
    print("  POSTing pet types to store #2...")
    for name, pet_type in [("id_4", PET_TYPE1), ("id_5", PET_TYPE2), ("id_6", PET_TYPE4)]:
        try:
            r = requests.post(
                f"{STORE2_URL}/pet-types",
                json=pet_type,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            if r.status_code == 201:
                ids[name] = r.json()["id"]
                print(f"    {name}: {ids[name]} ({pet_type['type']})")
            else:
                print(f"    Failed to create {pet_type['type']}: {r.status_code}")
        except Exception as e:
            print(f"    Error creating {pet_type['type']}: {e}")

    # Steps 3-4: POST pets to store #1
    print("  POSTing pets to store #1...")
    if "id_1" in ids:
        for pet in [PET1_TYPE1, PET2_TYPE1]:
            try:
                requests.post(
                    f"{STORE1_URL}/pet-types/{ids['id_1']}/pets",
                    json=pet,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                print(f"    Added {pet['name']} to id_1")
            except Exception as e:
                print(f"    Error adding {pet['name']}: {e}")

    if "id_3" in ids:
        for pet in [PET5_TYPE3, PET6_TYPE3]:
            try:
                requests.post(
                    f"{STORE1_URL}/pet-types/{ids['id_3']}/pets",
                    json=pet,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                print(f"    Added {pet['name']} to id_3")
            except Exception as e:
                print(f"    Error adding {pet['name']}: {e}")

    # Steps 5-7: POST pets to store #2
    print("  POSTing pets to store #2...")
    if "id_4" in ids:
        try:
            requests.post(
                f"{STORE2_URL}/pet-types/{ids['id_4']}/pets",
                json=PET3_TYPE1,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            print(f"    Added {PET3_TYPE1['name']} to id_4")
        except Exception as e:
            print(f"    Error adding {PET3_TYPE1['name']}: {e}")

    if "id_5" in ids:
        try:
            requests.post(
                f"{STORE2_URL}/pet-types/{ids['id_5']}/pets",
                json=PET4_TYPE2,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            print(f"    Added {PET4_TYPE2['name']} to id_5")
        except Exception as e:
            print(f"    Error adding {PET4_TYPE2['name']}: {e}")

    if "id_6" in ids:
        for pet in [PET7_TYPE4, PET8_TYPE4]:
            try:
                requests.post(
                    f"{STORE2_URL}/pet-types/{ids['id_6']}/pets",
                    json=pet,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                print(f"    Added {pet['name']} to id_6")
            except Exception as e:
                print(f"    Error adding {pet['name']}: {e}")

    print(f"Data population complete. IDs: {ids}")
    return ids


def parse_query_file(filepath):
    """
    Parse query.txt and return list of commands.

    Query format: "query: <pet-store-num>,<field>=<value>;"
    Purchase format: "purchase: <JSON-purchase>;"
    """
    commands = []

    try:
        with open(filepath, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Warning: {filepath} not found")
        return commands

    # Split by semicolons
    parts = content.split(';')

    for part in parts:
        part = part.strip()
        if not part:
            continue

        if part.startswith('query:'):
            # Format: query: <store>,<field>=<value>
            query_part = part[6:].strip()  # Remove "query:"

            # Parse store number and query string
            if ',' in query_part:
                store_str, query_str = query_part.split(',', 1)
                store_num = int(store_str.strip())

                # Parse field=value
                if '=' in query_str:
                    field, value = query_str.split('=', 1)
                    commands.append({
                        'type': 'query',
                        'store': store_num,
                        'field': field.strip(),
                        'value': value.strip()
                    })

        elif part.startswith('purchase:'):
            # Format: purchase: <JSON>
            json_part = part[9:].strip()  # Remove "purchase:"
            try:
                purchase_data = json.loads(json_part)
                commands.append({
                    'type': 'purchase',
                    'data': purchase_data
                })
            except json.JSONDecodeError as e:
                print(f"Error parsing purchase JSON: {e}")

    return commands


def execute_query(store, field, value):
    """
    Execute a GET /pet-types query against a store.
    Returns (status_code, payload).
    """
    store_url = STORE1_URL if store == 1 else STORE2_URL

    try:
        response = requests.get(
            f"{store_url}/pet-types",
            params={field: value},
            timeout=10
        )
        if response.status_code == 200:
            return response.status_code, response.json()
        else:
            return response.status_code, None
    except Exception as e:
        print(f"Error executing query: {e}")
        return 500, None


def execute_purchase(data):
    """
    Execute a POST /purchases request.
    Returns (status_code, payload).
    """
    try:
        response = requests.post(
            f"{ORDER_URL}/purchases",
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        if response.status_code == 201:
            return response.status_code, response.json()
        else:
            return response.status_code, None
    except Exception as e:
        print(f"Error executing purchase: {e}")
        return 500, None


def main():
    """Main entry point."""
    print("=" * 50)
    print("Query Processor for Assignment 4")
    print("=" * 50)

    # Wait for services
    if not wait_for_services():
        print("Exiting due to service unavailability")
        sys.exit(1)

    # Populate data (same as pytest steps 1-7)
    populate_data()
    time.sleep(2)  # Allow time for data to be indexed

    # Parse query file
    print("\nParsing query.txt...")
    commands = parse_query_file("query.txt")
    print(f"Found {len(commands)} commands")

    # Execute commands and collect results
    results = []
    for i, cmd in enumerate(commands):
        print(f"\nExecuting command {i+1}/{len(commands)}: {cmd['type']}")

        if cmd['type'] == 'query':
            status, payload = execute_query(
                cmd['store'], cmd['field'], cmd['value']
            )
            print(f"  Store {cmd['store']}, {cmd['field']}={cmd['value']} -> {status}")
        elif cmd['type'] == 'purchase':
            status, payload = execute_purchase(cmd['data'])
            print(f"  Purchase -> {status}")
        else:
            continue

        # Format result according to spec
        # <status-code><nl><payload><nl>;
        if payload is None:
            result_str = f"{status}\nNONE\n;"
        else:
            result_str = f"{status}\n{json.dumps(payload, indent=2)}\n;"

        results.append(result_str)

    # Write response.txt
    print("\nWriting response.txt...")
    with open("response.txt", "w") as f:
        f.write("\n".join(results))

    print("Done!")
    print("=" * 50)


if __name__ == "__main__":
    main()
