import io
import json


def _make_test_png():
    """Build a minimal valid 10x10 red PNG in memory, no external deps."""
    import struct
    import zlib

    width, height = 10, 10

    def chunk(tag, data):
        c = tag + data
        return struct.pack("!I", len(data)) + c + struct.pack("!I", zlib.crc32(c))

    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack("!IIBBBBB", width, height, 8, 2, 0, 0, 0)
    raw = b""
    for _ in range(height):
        raw += b"\x00" + bytes([255, 0, 0] * width)
    idat = zlib.compress(raw)

    buf = io.BytesIO()
    buf.write(sig)
    buf.write(chunk(b"IHDR", ihdr))
    buf.write(chunk(b"IDAT", idat))
    buf.write(chunk(b"IEND", b""))
    buf.seek(0)
    return buf


# ---------- health ----------

def test_health(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.get_json()["status"] == "ok"


# ---------- CRUD ----------

def test_create_item_requires_title_and_category(client):
    res = client.post("/api/items", json={"creator": "No Title Here"})
    assert res.status_code == 400
    assert "error" in res.get_json()


def test_create_item_rejects_invalid_category(client, sample_item_payload):
    sample_item_payload["category"] = "not-a-real-category"
    res = client.post("/api/items", json=sample_item_payload)
    assert res.status_code == 400


def test_create_and_get_item(client, sample_item_payload):
    res = client.post("/api/items", json=sample_item_payload)
    assert res.status_code == 201
    created = res.get_json()
    assert created["title"] == sample_item_payload["title"]
    assert created["tags"] == ["test", "sample"]

    res = client.get(f"/api/items/{created['id']}")
    assert res.status_code == 200
    assert res.get_json()["accession_number"] == "TST-0001"


def test_get_nonexistent_item_404s(client):
    res = client.get("/api/items/99999")
    assert res.status_code == 404


def test_update_item(client, sample_item_payload):
    created = client.post("/api/items", json=sample_item_payload).get_json()
    res = client.put(f"/api/items/{created['id']}", json={"title": "Updated Title", "condition": "excellent"})
    assert res.status_code == 200
    updated = res.get_json()
    assert updated["title"] == "Updated Title"
    assert updated["condition"] == "excellent"
    # untouched fields should survive the partial update
    assert updated["accession_number"] == "TST-0001"


def test_delete_item(client, sample_item_payload):
    created = client.post("/api/items", json=sample_item_payload).get_json()
    res = client.delete(f"/api/items/{created['id']}")
    assert res.status_code == 204
    assert client.get(f"/api/items/{created['id']}").status_code == 404


# ---------- search & filter ----------

def test_search_by_keyword(client, sample_item_payload):
    client.post("/api/items", json=sample_item_payload)
    client.post("/api/items", json={**sample_item_payload, "title": "Unrelated Photo",
                                     "category": "photo", "accession_number": "TST-0002",
                                     "tags": ["other"]})

    res = client.get("/api/items?q=Codex")
    data = res.get_json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Test Codex"


def test_filter_by_category(client, sample_item_payload):
    client.post("/api/items", json=sample_item_payload)
    client.post("/api/items", json={**sample_item_payload, "title": "A Photo",
                                     "category": "photo", "accession_number": "TST-0003"})

    res = client.get("/api/items?category=photo")
    data = res.get_json()
    assert data["total"] == 1
    assert data["items"][0]["category"] == "photo"


# ---------- CSV import / export ----------

def test_csv_import_creates_items_and_reports_errors(client):
    csv_content = (
        "title,category,creator,accession_number\n"
        "Good Row,book,Author A,CSV-0001\n"
        "Bad Category Row,not-a-category,Author B,CSV-0002\n"
        ",archive,Author C,CSV-0003\n"  # missing title
    )
    data = {"file": (io.BytesIO(csv_content.encode()), "import.csv")}
    res = client.post("/api/items/import", data=data, content_type="multipart/form-data")
    assert res.status_code == 200
    body = res.get_json()
    assert body["created_count"] == 1
    assert body["error_count"] == 2


def test_csv_export_contains_created_item(client, sample_item_payload):
    client.post("/api/items", json=sample_item_payload)
    res = client.get("/api/items/export")
    assert res.status_code == 200
    assert b"Test Codex" in res.data


# ---------- validation report ----------

def test_validate_flags_missing_accession_number(client, sample_item_payload):
    payload = {**sample_item_payload, "accession_number": ""}
    client.post("/api/items", json=payload)

    res = client.get("/api/items/validate")
    assert res.status_code == 200
    body = res.get_json()
    assert body["total_records"] == 1
    assert len(body["record_issues"]) == 1
    assert "missing accession number" in body["record_issues"][0]["problems"]


def test_validate_flags_duplicate_accession_numbers(client, sample_item_payload):
    client.post("/api/items", json=sample_item_payload)
    client.post("/api/items", json={**sample_item_payload, "title": "Duplicate Codex"})

    res = client.get("/api/items/validate")
    body = res.get_json()
    assert "TST-0001" in body["duplicate_accession_numbers"]


# ---------- image upload ----------

def test_upload_and_delete_image(client, sample_item_payload):
    created = client.post("/api/items", json=sample_item_payload).get_json()

    png = _make_test_png()
    data = {"image": (png, "test.png")}
    res = client.post(f"/api/items/{created['id']}/image", data=data, content_type="multipart/form-data")
    assert res.status_code == 200
    updated = res.get_json()
    assert updated["image_url"] is not None
    assert updated["image_url"].startswith("/uploads/")

    # the uploaded file should actually be servable
    filename = updated["image_url"].split("/")[-1]
    res = client.get(f"/uploads/{filename}")
    assert res.status_code == 200

    # deleting should clear the image_url
    res = client.delete(f"/api/items/{created['id']}/image")
    assert res.status_code == 200
    assert res.get_json()["image_url"] is None


def test_upload_rejects_disallowed_file_type(client, sample_item_payload):
    created = client.post("/api/items", json=sample_item_payload).get_json()
    data = {"image": (io.BytesIO(b"not an image"), "notes.txt")}
    res = client.post(f"/api/items/{created['id']}/image", data=data, content_type="multipart/form-data")
    assert res.status_code == 400
