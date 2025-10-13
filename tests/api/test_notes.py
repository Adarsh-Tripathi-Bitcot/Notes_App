"""
API tests for notes endpoints.

This module contains tests for note CRUD operations, search, filtering,
and other note-related functionality in the Notes App API.
"""

from fastapi.testclient import TestClient


class TestNoteCreation:
    """Test note creation functionality."""

    def test_create_note_success(
        self, client: TestClient, auth_headers, sample_note_data
    ):
        """Test successful note creation."""
        response = client.post(
            "/api/v1/notes/", json=sample_note_data, headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == sample_note_data["title"]
        assert data["content"] == sample_note_data["content"]
        assert data["summary"] == sample_note_data["summary"]
        assert data["is_public"] == sample_note_data["is_public"]
        assert data["is_pinned"] == sample_note_data["is_pinned"]
        assert data["status"] == "active"
        assert "id" in data
        assert "created_at" in data
        assert "owner_id" in data

    def test_create_note_without_auth(self, client: TestClient, sample_note_data):
        """Test note creation without authentication."""
        response = client.post("/api/v1/notes/", json=sample_note_data)

        assert response.status_code == 401
        data = response.json()
        assert "error" in data

    def test_create_note_missing_title(
        self, client: TestClient, auth_headers, sample_note_data
    ):
        """Test note creation with missing title."""
        del sample_note_data["title"]

        response = client.post(
            "/api/v1/notes/", json=sample_note_data, headers=auth_headers
        )

        assert response.status_code == 422
        data = response.json()
        assert "error" in data

    def test_create_note_missing_content(
        self, client: TestClient, auth_headers, sample_note_data
    ):
        """Test note creation with missing content."""
        del sample_note_data["content"]

        response = client.post(
            "/api/v1/notes/", json=sample_note_data, headers=auth_headers
        )

        assert response.status_code == 422
        data = response.json()
        assert "error" in data

    def test_create_note_empty_title(
        self, client: TestClient, auth_headers, sample_note_data
    ):
        """Test note creation with empty title."""
        sample_note_data["title"] = ""

        response = client.post(
            "/api/v1/notes/", json=sample_note_data, headers=auth_headers
        )

        assert response.status_code == 422
        data = response.json()
        assert "error" in data

    def test_create_note_empty_content(
        self, client: TestClient, auth_headers, sample_note_data
    ):
        """Test note creation with empty content."""
        sample_note_data["content"] = ""

        response = client.post(
            "/api/v1/notes/", json=sample_note_data, headers=auth_headers
        )

        assert response.status_code == 422
        data = response.json()
        assert "error" in data


class TestNoteRetrieval:
    """Test note retrieval functionality."""

    def test_get_notes_success(self, client: TestClient, auth_headers, test_note):
        """Test successful notes retrieval."""
        response = client.get("/api/v1/notes/", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "notes" in data
        assert "total" in data
        assert "page" in data
        assert "per_page" in data
        assert "total_pages" in data
        assert len(data["notes"]) >= 1
        assert data["total"] >= 1

    def test_get_notes_without_auth(self, client: TestClient):
        """Test notes retrieval without authentication."""
        response = client.get("/api/v1/notes/")

        assert response.status_code == 401
        data = response.json()
        assert "error" in data

    def test_get_notes_pagination(self, client: TestClient, auth_headers, test_note):
        """Test notes retrieval with pagination."""
        response = client.get("/api/v1/notes/?page=1&per_page=5", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["per_page"] == 5
        assert len(data["notes"]) <= 5

    def test_get_notes_filter_by_status(
        self, client: TestClient, auth_headers, test_note
    ):
        """Test notes retrieval filtered by status."""
        response = client.get("/api/v1/notes/?status=active", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        for note in data["notes"]:
            assert note["status"] == "active"

    def test_get_notes_search(self, client: TestClient, auth_headers, test_note):
        """Test notes retrieval with search query."""
        response = client.get("/api/v1/notes/?search=Test", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        # Should find the test note
        assert data["total"] >= 1

    def test_get_specific_note_success(
        self, client: TestClient, auth_headers, test_note
    ):
        """Test successful specific note retrieval."""
        response = client.get(f"/api/v1/notes/{test_note.id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_note.id
        assert data["title"] == test_note.title
        assert data["content"] == test_note.content

    def test_get_specific_note_not_found(self, client: TestClient, auth_headers):
        """Test specific note retrieval with non-existent note."""
        response = client.get("/api/v1/notes/99999", headers=auth_headers)

        assert response.status_code == 404
        data = response.json()
        assert "error" in data

    def test_get_specific_note_without_auth(self, client: TestClient, test_note):
        """Test specific note retrieval without authentication."""
        response = client.get(f"/api/v1/notes/{test_note.id}")

        assert response.status_code == 401
        data = response.json()
        assert "error" in data


class TestNoteUpdate:
    """Test note update functionality."""

    def test_update_note_success(self, client: TestClient, auth_headers, test_note):
        """Test successful note update."""
        update_data = {
            "title": "Updated Title",
            "content": "Updated content",
            "summary": "Updated summary",
        }

        response = client.put(
            f"/api/v1/notes/{test_note.id}", json=update_data, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["content"] == update_data["content"]
        assert data["summary"] == update_data["summary"]

    def test_update_note_partial(self, client: TestClient, auth_headers, test_note):
        """Test partial note update."""
        update_data = {"title": "Only Title Updated"}

        response = client.put(
            f"/api/v1/notes/{test_note.id}", json=update_data, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == update_data["title"]
        # Other fields should remain unchanged
        assert data["content"] == test_note.content

    def test_update_note_not_found(self, client: TestClient, auth_headers):
        """Test note update with non-existent note."""
        update_data = {"title": "Updated Title"}

        response = client.put(
            "/api/v1/notes/99999", json=update_data, headers=auth_headers
        )

        assert response.status_code == 404
        data = response.json()
        assert "error" in data

    def test_update_note_without_auth(self, client: TestClient, test_note):
        """Test note update without authentication."""
        update_data = {"title": "Updated Title"}

        response = client.put(f"/api/v1/notes/{test_note.id}", json=update_data)

        assert response.status_code == 401
        data = response.json()
        assert "error" in data

    def test_update_note_empty_title(self, client: TestClient, auth_headers, test_note):
        """Test note update with empty title."""
        update_data = {"title": ""}

        response = client.put(
            f"/api/v1/notes/{test_note.id}", json=update_data, headers=auth_headers
        )

        assert response.status_code == 422
        data = response.json()
        assert "error" in data


class TestNoteStatusUpdate:
    """Test note status update functionality."""

    def test_update_note_status_to_archived(
        self, client: TestClient, auth_headers, test_note
    ):
        """Test updating note status to archived."""
        status_data = {"status": "archived"}

        response = client.put(
            f"/api/v1/notes/{test_note.id}/status",
            json=status_data,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "archived"

    def test_update_note_status_to_active(
        self, client: TestClient, auth_headers, test_note, db_session
    ):
        """Test updating note status to active."""
        # First archive the note
        test_note.status = "archived"
        db_session.commit()

        status_data = {"status": "active"}

        response = client.put(
            f"/api/v1/notes/{test_note.id}/status",
            json=status_data,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "active"

    def test_update_note_status_invalid(
        self, client: TestClient, auth_headers, test_note
    ):
        """Test updating note status with invalid status."""
        status_data = {"status": "invalid_status"}

        response = client.put(
            f"/api/v1/notes/{test_note.id}/status",
            json=status_data,
            headers=auth_headers,
        )

        assert response.status_code == 422
        data = response.json()
        assert "error" in data

    def test_update_note_status_not_found(self, client: TestClient, auth_headers):
        """Test note status update with non-existent note."""
        status_data = {"status": "archived"}

        response = client.put(
            "/api/v1/notes/99999/status", json=status_data, headers=auth_headers
        )

        assert response.status_code == 404
        data = response.json()
        assert "error" in data


class TestNoteDeletion:
    """Test note deletion functionality."""

    def test_delete_note_success(self, client: TestClient, auth_headers, test_note):
        """Test successful note deletion."""
        response = client.delete(f"/api/v1/notes/{test_note.id}", headers=auth_headers)

        assert response.status_code == 204

    def test_delete_note_not_found(self, client: TestClient, auth_headers):
        """Test note deletion with non-existent note."""
        response = client.delete("/api/v1/notes/99999", headers=auth_headers)

        assert response.status_code == 404
        data = response.json()
        assert "error" in data

    def test_delete_note_without_auth(self, client: TestClient, test_note):
        """Test note deletion without authentication."""
        response = client.delete(f"/api/v1/notes/{test_note.id}")

        assert response.status_code == 401
        data = response.json()
        assert "error" in data


class TestPublicNotes:
    """Test public notes functionality."""

    def test_get_public_notes_success(
        self, client: TestClient, auth_headers, test_note, db_session
    ):
        """Test successful public notes retrieval."""
        # Make the test note public
        test_note.is_public = True
        db_session.commit()

        response = client.get("/api/v1/notes/public")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should find the public test note
        assert len(data) >= 1

    def test_get_public_notes_pagination(
        self, client: TestClient, test_note, db_session
    ):
        """Test public notes retrieval with pagination."""
        # Make the test note public
        test_note.is_public = True
        db_session.commit()

        response = client.get("/api/v1/notes/public?page=1&per_page=5")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5

    def test_get_public_notes_search(self, client: TestClient, test_note, db_session):
        """Test public notes retrieval with search."""
        # Make the test note public
        test_note.is_public = True
        db_session.commit()

        response = client.get("/api/v1/notes/public?search=Test")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestNoteSearch:
    """Test note search functionality."""

    def test_search_notes_success(self, client: TestClient, auth_headers, test_note):
        """Test successful note search."""
        search_data = {"query": "Test", "page": 1, "per_page": 10}

        response = client.post(
            "/api/v1/notes/search", json=search_data, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "notes" in data
        assert "total" in data
        assert "page" in data
        assert "per_page" in data
        assert "total_pages" in data

    def test_search_notes_without_auth(self, client: TestClient, test_note):
        """Test note search without authentication."""
        search_data = {"query": "Test", "page": 1, "per_page": 10}

        response = client.post("/api/v1/notes/search", json=search_data)

        assert response.status_code == 401
        data = response.json()
        assert "error" in data

    def test_search_notes_empty_query(self, client: TestClient, auth_headers):
        """Test note search with empty query."""
        search_data = {"query": "", "page": 1, "per_page": 10}

        response = client.post(
            "/api/v1/notes/search", json=search_data, headers=auth_headers
        )

        assert response.status_code == 422
        data = response.json()
        assert "error" in data
        # Should return validation error for empty query
        assert "validation" in data["error"]["message"].lower()


class TestNoteStats:
    """Test note statistics functionality."""

    def test_get_note_stats_success(self, client: TestClient, auth_headers, test_note):
        """Test successful note statistics retrieval."""
        response = client.get("/api/v1/notes/stats/overview", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "total_notes" in data
        assert "active_notes" in data
        assert "archived_notes" in data
        assert "public_notes" in data
        assert "pinned_notes" in data
        assert "created_today" in data
        assert "created_this_week" in data
        assert "created_this_month" in data

    def test_get_note_stats_without_auth(self, client: TestClient):
        """Test note statistics retrieval without authentication."""
        response = client.get("/api/v1/notes/stats/overview")

        assert response.status_code == 401
        data = response.json()
        assert "error" in data


class TestBulkActions:
    """Test bulk actions functionality."""

    def test_bulk_archive_notes(self, client: TestClient, auth_headers, test_note):
        """Test bulk archiving notes."""
        bulk_data = {"note_ids": [test_note.id], "action": "archive"}

        response = client.post(
            "/api/v1/notes/bulk-action", json=bulk_data, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "affected_count" in data
        assert data["affected_count"] >= 1

    def test_bulk_pin_notes(self, client: TestClient, auth_headers, test_note):
        """Test bulk pinning notes."""
        bulk_data = {"note_ids": [test_note.id], "action": "pin"}

        response = client.post(
            "/api/v1/notes/bulk-action", json=bulk_data, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "affected_count" in data

    def test_bulk_action_invalid_action(
        self, client: TestClient, auth_headers, test_note
    ):
        """Test bulk action with invalid action."""
        bulk_data = {"note_ids": [test_note.id], "action": "invalid_action"}

        response = client.post(
            "/api/v1/notes/bulk-action", json=bulk_data, headers=auth_headers
        )

        assert response.status_code == 422
        data = response.json()
        assert "error" in data

    def test_bulk_action_empty_note_ids(self, client: TestClient, auth_headers):
        """Test bulk action with empty note IDs."""
        bulk_data = {"note_ids": [], "action": "archive"}

        response = client.post(
            "/api/v1/notes/bulk-action", json=bulk_data, headers=auth_headers
        )

        assert response.status_code == 422
        data = response.json()
        assert "error" in data

    def test_bulk_action_without_auth(self, client: TestClient, test_note):
        """Test bulk action without authentication."""
        bulk_data = {"note_ids": [test_note.id], "action": "archive"}

        response = client.post("/api/v1/notes/bulk-action", json=bulk_data)

        assert response.status_code == 401
        data = response.json()
        assert "error" in data
