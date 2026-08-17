import os
import tempfile
import shutil

import pytest


@pytest.fixture
def app():
    """Create a Flask app instance wired to a throwaway SQLite file and
    upload folder, so tests never touch the real dev database or uploads."""
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    upload_dir = tempfile.mkdtemp()

    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
    os.environ["UPLOAD_FOLDER"] = upload_dir

    # Import after env vars are set so create_app() picks them up.
    from app import create_app

    flask_app = create_app()
    flask_app.config.update(TESTING=True)

    yield flask_app

    os.close(db_fd)
    os.remove(db_path)
    shutil.rmtree(upload_dir, ignore_errors=True)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def sample_item_payload():
    return {
        "title": "Test Codex",
        "category": "book",
        "creator": "Jane Doe",
        "donor": "Test Donor",
        "accession_number": "TST-0001",
        "condition": "good",
        "location": "Shelf Z9",
        "description": "A sample item created during a test run.",
        "tags": ["test", "sample"],
    }
