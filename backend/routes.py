import csv
import io
import os
import uuid
from flask import Blueprint, request, jsonify, Response, current_app
from sqlalchemy import or_
from werkzeug.utils import secure_filename
from models import db, Item

api = Blueprint("api", __name__)

VALID_CATEGORIES = {"book", "archive", "photo", "artifact", "other"}
REQUIRED_IMPORT_FIELDS = {"title", "category"}
ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


def _allowed_image(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


# ---------- CRUD ----------

@api.route("/items", methods=["GET"])
def list_items():
    """List items with optional search/filter/pagination.

    Query params:
      q          - keyword search across title, creator, description, tags
      category   - filter by category
      condition  - filter by condition
      public_only - "true" to restrict to publicly visible items
      page, per_page - pagination
    """
    query = Item.query

    q = request.args.get("q")
    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                Item.title.ilike(like),
                Item.creator.ilike(like),
                Item.description.ilike(like),
                Item.tags.ilike(like),
                Item.accession_number.ilike(like),
            )
        )

    category = request.args.get("category")
    if category:
        query = query.filter(Item.category == category)

    condition = request.args.get("condition")
    if condition:
        query = query.filter(Item.condition == condition)

    if request.args.get("public_only") == "true":
        query = query.filter(Item.is_public.is_(True))

    page = int(request.args.get("page", 1))
    per_page = min(int(request.args.get("per_page", 25)), 100)

    pagination = query.order_by(Item.date_added.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        "items": [i.to_dict() for i in pagination.items],
        "total": pagination.total,
        "page": page,
        "pages": pagination.pages,
    })


@api.route("/items/<int:item_id>", methods=["GET"])
def get_item(item_id):
    item = Item.query.get_or_404(item_id)
    return jsonify(item.to_dict())


@api.route("/items", methods=["POST"])
def create_item():
    data = request.get_json(force=True)
    error = _validate_item(data)
    if error:
        return jsonify({"error": error}), 400

    item = Item(
        title=data["title"].strip(),
        category=data["category"],
        creator=data.get("creator", "").strip() or None,
        donor=data.get("donor", "").strip() or None,
        accession_number=data.get("accession_number", "").strip() or None,
        condition=data.get("condition") or None,
        location=data.get("location", "").strip() or None,
        description=data.get("description", "").strip() or None,
        tags=",".join(data.get("tags", [])) if isinstance(data.get("tags"), list) else data.get("tags"),
        is_public=data.get("is_public", True),
    )
    db.session.add(item)
    db.session.commit()
    return jsonify(item.to_dict()), 201


@api.route("/items/<int:item_id>", methods=["PUT"])
def update_item(item_id):
    item = Item.query.get_or_404(item_id)
    data = request.get_json(force=True)
    error = _validate_item(data, is_update=True)
    if error:
        return jsonify({"error": error}), 400

    for field in ["title", "category", "creator", "donor", "accession_number",
                  "condition", "location", "description", "is_public"]:
        if field in data:
            setattr(item, field, data[field])

    if "tags" in data:
        tags = data["tags"]
        item.tags = ",".join(tags) if isinstance(tags, list) else tags

    db.session.commit()
    return jsonify(item.to_dict())


@api.route("/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    _delete_image_file(item.image_filename)
    db.session.delete(item)
    db.session.commit()
    return "", 204


# ---------- Image upload ----------

@api.route("/items/<int:item_id>/image", methods=["POST"])
def upload_image(item_id):
    """Upload/replace the thumbnail image for an item.

    Send as multipart/form-data with field 'image'. Replaces any existing
    image file for this item.
    """
    item = Item.query.get_or_404(item_id)

    if "image" not in request.files:
        return jsonify({"error": "No file uploaded. Send as multipart/form-data field 'image'."}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "No file selected."}), 400
    if not _allowed_image(file.filename):
        return jsonify({"error": f"Unsupported file type. Allowed: {', '.join(sorted(ALLOWED_IMAGE_EXTENSIONS))}"}), 400

    # remove the old image file, if any, before saving the new one
    _delete_image_file(item.image_filename)

    ext = secure_filename(file.filename).rsplit(".", 1)[1].lower()
    new_filename = f"{uuid.uuid4().hex}.{ext}"
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)
    file.save(os.path.join(upload_folder, new_filename))

    item.image_filename = new_filename
    db.session.commit()
    return jsonify(item.to_dict())


@api.route("/items/<int:item_id>/image", methods=["DELETE"])
def delete_image(item_id):
    item = Item.query.get_or_404(item_id)
    _delete_image_file(item.image_filename)
    item.image_filename = None
    db.session.commit()
    return jsonify(item.to_dict())


def _delete_image_file(filename):
    if not filename:
        return
    path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    if os.path.exists(path):
        os.remove(path)


# ---------- Bulk CSV import ----------

@api.route("/items/import", methods=["POST"])
def import_csv():
    """Bulk import items from an uploaded CSV file.

    Expected columns (header row required): title, category, creator, donor,
    accession_number, condition, location, description, tags
    Returns a report of created rows and any validation errors, so bad rows
    don't silently get skipped.
    """
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded. Send as multipart/form-data field 'file'."}), 400

    file = request.files["file"]
    stream = io.StringIO(file.stream.read().decode("utf-8-sig"))
    reader = csv.DictReader(stream)

    created, errors = [], []
    existing_accession_numbers = {
        a for (a,) in db.session.query(Item.accession_number).filter(Item.accession_number.isnot(None))
    }

    for row_num, row in enumerate(reader, start=2):  # row 1 is header
        row = {k.strip().lower(): (v.strip() if v else v) for k, v in row.items()}
        error = _validate_item(row)
        if error:
            errors.append({"row": row_num, "error": error, "data": row})
            continue

        accession = row.get("accession_number") or None
        if accession and accession in existing_accession_numbers:
            errors.append({"row": row_num, "error": f"Duplicate accession_number '{accession}'", "data": row})
            continue
        if accession:
            existing_accession_numbers.add(accession)

        item = Item(
            title=row["title"],
            category=row["category"],
            creator=row.get("creator") or None,
            donor=row.get("donor") or None,
            accession_number=accession,
            condition=row.get("condition") or None,
            location=row.get("location") or None,
            description=row.get("description") or None,
            tags=row.get("tags") or None,
            is_public=str(row.get("is_public", "true")).lower() != "false",
        )
        db.session.add(item)
        created.append(row_num)

    db.session.commit()
    return jsonify({
        "created_count": len(created),
        "error_count": len(errors),
        "errors": errors,
    })


# ---------- Data validation report ----------

@api.route("/items/validate", methods=["GET"])
def validate_catalog():
    """Scan existing records for issues: missing fields, duplicate accession
    numbers, or unrecognized categories -- mirrors the SQL validation
    workflow used for the museum catalog."""
    issues = []

    for item in Item.query.all():
        problems = []
        if not item.title:
            problems.append("missing title")
        if item.category not in VALID_CATEGORIES:
            problems.append(f"unrecognized category '{item.category}'")
        if not item.accession_number:
            problems.append("missing accession number")
        if problems:
            issues.append({"id": item.id, "title": item.title, "problems": problems})

    # duplicate accession numbers
    seen, dupes = {}, set()
    for item in Item.query.filter(Item.accession_number.isnot(None)).all():
        if item.accession_number in seen:
            dupes.add(item.accession_number)
        seen[item.accession_number] = item.id

    return jsonify({
        "record_issues": issues,
        "duplicate_accession_numbers": list(dupes),
        "total_records": Item.query.count(),
    })


# ---------- Export ----------

@api.route("/items/export", methods=["GET"])
def export_csv():
    items = Item.query.order_by(Item.date_added.desc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["title", "category", "creator", "donor", "accession_number",
                      "condition", "location", "description", "tags", "is_public"])
    for i in items:
        writer.writerow([i.title, i.category, i.creator, i.donor, i.accession_number,
                          i.condition, i.location, i.description, i.tags, i.is_public])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=catalog_export.csv"},
    )


# ---------- helpers ----------

def _validate_item(data, is_update=False):
    if not is_update:
        missing = REQUIRED_IMPORT_FIELDS - set(k for k, v in data.items() if v)
        if missing:
            return f"Missing required field(s): {', '.join(sorted(missing))}"
    category = data.get("category")
    if category and category not in VALID_CATEGORIES:
        return f"Invalid category '{category}'. Must be one of: {', '.join(sorted(VALID_CATEGORIES))}"
    return None
