from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Item(db.Model):
    """A single catalog item (book, archive, photo, artifact, etc.)."""

    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # book, archive, photo, artifact, other
    creator = db.Column(db.String(255))  # author / artist / origin
    donor = db.Column(db.String(255))
    accession_number = db.Column(db.String(100))  # intentionally not DB-unique — see /api/items/validate
    condition = db.Column(db.String(50))  # excellent, good, fair, poor
    location = db.Column(db.String(120))  # physical storage location
    description = db.Column(db.Text)
    tags = db.Column(db.String(255))  # comma-separated for simple search/filtering
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    is_public = db.Column(db.Boolean, default=True)  # visible on public catalog view
    image_filename = db.Column(db.String(255))  # stored filename in the uploads folder

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "category": self.category,
            "creator": self.creator,
            "donor": self.donor,
            "accession_number": self.accession_number,
            "condition": self.condition,
            "location": self.location,
            "description": self.description,
            "tags": [t.strip() for t in self.tags.split(",")] if self.tags else [],
            "date_added": self.date_added.isoformat() if self.date_added else None,
            "is_public": self.is_public,
            "image_url": f"/uploads/{self.image_filename}" if self.image_filename else None,
        }
