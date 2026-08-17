import { useEffect, useState } from "react";
import { deleteItemImage } from "../api";

const EMPTY_ITEM = {
  title: "",
  category: "book",
  creator: "",
  donor: "",
  accession_number: "",
  condition: "",
  location: "",
  description: "",
  tags: "",
  is_public: true,
};

export default function ItemForm({ item, onSave, onCancel }) {
  const [form, setForm] = useState(EMPTY_ITEM);
  const [error, setError] = useState(null);
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [existingImageUrl, setExistingImageUrl] = useState(null);
  const [removeExistingImage, setRemoveExistingImage] = useState(false);

  useEffect(() => {
    if (item) {
      setForm({ ...EMPTY_ITEM, ...item, tags: (item.tags || []).join(", ") });
      setExistingImageUrl(item.image_url || null);
    } else {
      setForm(EMPTY_ITEM);
      setExistingImageUrl(null);
    }
    setImageFile(null);
    setImagePreview(null);
    setRemoveExistingImage(false);
  }, [item]);

  const handle = (field) => (e) => {
    const value = field === "is_public" ? e.target.checked : e.target.value;
    setForm({ ...form, [field]: value });
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setImageFile(file);
    setRemoveExistingImage(false);
    setImagePreview(URL.createObjectURL(file));
  };

  const handleRemoveImage = async () => {
    setImageFile(null);
    setImagePreview(null);
    if (item && existingImageUrl) {
      // existing item with a saved image: mark for deletion on save
      setRemoveExistingImage(true);
      setExistingImageUrl(null);
    }
  };

  const submit = async (e) => {
    e.preventDefault();
    if (!form.title.trim() || !form.category) {
      setError("Title and category are required.");
      return;
    }
    setError(null);

    if (removeExistingImage && item) {
      await deleteItemImage(item.id);
    }

    onSave(
      {
        ...form,
        tags: form.tags
          .split(",")
          .map((t) => t.trim())
          .filter(Boolean),
      },
      imageFile
    );
  };

  return (
    <div className="modal d-block" tabIndex="-1" style={{ background: "rgba(0,0,0,0.5)" }}>
      <div className="modal-dialog modal-lg">
        <div className="modal-content">
          <form onSubmit={submit}>
            <div className="modal-header">
              <h5 className="modal-title">{item ? "Edit Item" : "Add New Item"}</h5>
              <button type="button" className="btn-close" onClick={onCancel} />
            </div>
            <div className="modal-body">
              {error && <div className="alert alert-danger">{error}</div>}

              <div className="row g-3">
                <div className="col-md-8">
                  <label className="form-label">Title *</label>
                  <input className="form-control" value={form.title} onChange={handle("title")} required />
                </div>
                <div className="col-md-4">
                  <label className="form-label">Category *</label>
                  <select className="form-select" value={form.category} onChange={handle("category")}>
                    <option value="book">Book</option>
                    <option value="archive">Archive</option>
                    <option value="photo">Photo</option>
                    <option value="artifact">Artifact</option>
                    <option value="other">Other</option>
                  </select>
                </div>

                <div className="col-md-6">
                  <label className="form-label">Creator</label>
                  <input className="form-control" value={form.creator || ""} onChange={handle("creator")} />
                </div>
                <div className="col-md-6">
                  <label className="form-label">Donor</label>
                  <input className="form-control" value={form.donor || ""} onChange={handle("donor")} />
                </div>

                <div className="col-md-4">
                  <label className="form-label">Accession #</label>
                  <input
                    className="form-control"
                    value={form.accession_number || ""}
                    onChange={handle("accession_number")}
                  />
                </div>
                <div className="col-md-4">
                  <label className="form-label">Condition</label>
                  <select className="form-select" value={form.condition || ""} onChange={handle("condition")}>
                    <option value="">-- Select --</option>
                    <option value="excellent">Excellent</option>
                    <option value="good">Good</option>
                    <option value="fair">Fair</option>
                    <option value="poor">Poor</option>
                  </select>
                </div>
                <div className="col-md-4">
                  <label className="form-label">Location</label>
                  <input className="form-control" value={form.location || ""} onChange={handle("location")} />
                </div>

                <div className="col-12">
                  <label className="form-label">Description</label>
                  <textarea
                    className="form-control"
                    rows="3"
                    value={form.description || ""}
                    onChange={handle("description")}
                  />
                </div>

                <div className="col-md-8">
                  <label className="form-label">Tags (comma-separated)</label>
                  <input className="form-control" value={form.tags} onChange={handle("tags")} />
                </div>
                <div className="col-md-4 d-flex align-items-end">
                  <div className="form-check">
                    <input
                      className="form-check-input"
                      type="checkbox"
                      checked={form.is_public}
                      onChange={handle("is_public")}
                      id="isPublicCheck"
                    />
                    <label className="form-check-label" htmlFor="isPublicCheck">
                      Visible on public catalog
                    </label>
                  </div>
                </div>

                <div className="col-12">
                  <label className="form-label">Image</label>
                  <div className="d-flex align-items-center gap-3">
                    {(imagePreview || existingImageUrl) && (
                      <img
                        src={imagePreview || existingImageUrl}
                        alt="Preview"
                        className="rounded border"
                        style={{ width: 90, height: 90, objectFit: "cover" }}
                      />
                    )}
                    <div>
                      <input
                        type="file"
                        accept="image/png,image/jpeg,image/gif,image/webp"
                        className="form-control form-control-sm"
                        onChange={handleImageChange}
                      />
                      {(imagePreview || existingImageUrl) && (
                        <button
                          type="button"
                          className="btn btn-sm btn-link text-danger ps-0"
                          onClick={handleRemoveImage}
                        >
                          Remove image
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div className="modal-footer">
              <button type="button" className="btn btn-outline-secondary" onClick={onCancel}>
                Cancel
              </button>
              <button type="submit" className="btn btn-dark">
                {item ? "Save Changes" : "Add Item"}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
