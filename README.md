# Digital Collections Manager

A full-stack catalog application for archiving and searching collections —
books, archives, photos, and artifacts. Built to mirror a real museum
cataloging workflow: bulk import, data validation, and a searchable public
view alongside a staff management interface.

## Stack

- **Frontend:** React (Vite) + Bootstrap
- **Backend:** Flask + SQLAlchemy (REST API)
- **Database:** SQLite (swap `DATABASE_URL` for Postgres in production)
- **Containerization:** Docker / docker-compose

## Features

- Full CRUD for catalog items (title, category, creator, donor, accession
  number, condition, location, tags, description)
- **Image upload** — attach/replace/remove a thumbnail photo per item,
  served from the backend and shown on catalog cards
- Keyword search + filter by category/condition
- **Bulk CSV import** with a per-row error report (bad rows are reported,
  not silently dropped)
- CSV export
- **Data validation** endpoint that scans for missing fields, unrecognized
  categories, and duplicate accession numbers
- Public/private visibility flag per item

## Project structure

```
digital-collections-manager/
├── .github/
│   └── workflows/
│       └── ci.yml       # GitHub Actions: backend tests + frontend build
├── backend/
│   ├── app.py          # Flask app factory
│   ├── models.py       # SQLAlchemy Item model
│   ├── routes.py       # REST API endpoints
│   ├── seed.py         # sample data for local dev
│   ├── tests/           # pytest suite
│   ├── pytest.ini
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── api.js
│   │   └── components/
│   │       ├── SearchBar.jsx
│   │       ├── ItemList.jsx
│   │       ├── ItemForm.jsx
│   │       └── ImportCSV.jsx
│   ├── package.json
│   ├── vite.config.js
│   └── Dockerfile
└── docker-compose.yml
```

## Running locally (without Docker)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python seed.py             # optional: adds sample items
python app.py               # runs on http://localhost:5000
```

### Frontend

```bash
cd frontend
npm install
npm run dev                 # runs on http://localhost:5173
```

The Vite dev server proxies `/api` requests to `http://localhost:5000`, so
just open `http://localhost:5173` once both are running.

## Running with Docker

```bash
docker-compose up --build
```

- Frontend: http://localhost:5173
- Backend API: http://localhost:5000/api

**Note on container networking:** inside the frontend container, `localhost`
refers to the frontend container itself, not the backend. So the Vite dev
proxy needs to target the backend by its Docker Compose service name
(`http://backend:5000`) instead of `localhost:5000`. This is handled via the
`VITE_API_TARGET` environment variable, already set in `docker-compose.yml`.
If you ever add more services or rename `backend` in `docker-compose.yml`,
update that variable to match.

## Testing

The backend has a pytest suite covering CRUD, search/filter, CSV import/export,
data validation, and image upload — each test runs against an isolated
temporary SQLite database and upload folder, so nothing touches your real
dev data.

```bash
cd backend
pip install -r requirements-dev.txt
pytest -v
```

Add `--cov=. --cov-report=term-missing` to see a coverage breakdown.

## Continuous Integration

`.github/workflows/ci.yml` runs on every push and pull request to `main`:

- **Backend tests** — installs dependencies and runs the full pytest suite,
  with a coverage report uploaded as a build artifact
- **Frontend build** — installs dependencies with `npm ci` and runs
  `npm run build` to catch build-breaking errors before merge

Both jobs run independently and in parallel, so a frontend build failure
won't block you from seeing backend test results (and vice versa).

## API reference

| Method | Endpoint              | Description                              |
|--------|------------------------|-------------------------------------------|
| GET    | `/api/items`           | List/search items (`q`, `category`, `condition`, `page`, `per_page`) |
| GET    | `/api/items/<id>`      | Get a single item                        |
| POST   | `/api/items`           | Create an item                           |
| PUT    | `/api/items/<id>`      | Update an item                           |
| DELETE | `/api/items/<id>`      | Delete an item                           |
| POST   | `/api/items/import`    | Bulk import from CSV (`multipart/form-data`, field `file`) |
| GET    | `/api/items/export`    | Download all items as CSV                |
| GET    | `/api/items/validate`  | Data-quality report (missing fields, duplicate accession numbers) |
| POST   | `/api/items/<id>/image`| Upload/replace an item's image (`multipart/form-data`, field `image`, max 8MB) |
| DELETE | `/api/items/<id>/image`| Remove an item's image                   |
| GET    | `/uploads/<filename>`  | Serve an uploaded image file             |

### CSV import format

Header row required, columns:
```
title,category,creator,donor,accession_number,condition,location,description,tags
```
`category` must be one of: `book`, `archive`, `photo`, `artifact`, `other`.

## Next steps / ideas for extending this

- ISBN/barcode lookup auto-fill for books via a free API
- Role-based auth (staff vs. public viewer) instead of a simple public flag
- Deploy backend + frontend to Render/Railway or Kubernetes/OpenShift
- Swap local disk storage for S3-compatible object storage for images
