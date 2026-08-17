const CONDITION_BADGE = {
  excellent: "success",
  good: "primary",
  fair: "warning",
  poor: "danger",
};

export default function ItemList({ items, onEdit, onDelete }) {
  if (items.length === 0) {
    return <p className="text-muted text-center py-5">No items match your search.</p>;
  }

  return (
    <div className="row g-3">
      {items.map((item) => (
        <div className="col-md-6 col-lg-4" key={item.id}>
          <div className="card item-card h-100 shadow-sm">
            {item.image_url && (
              <img
                src={item.image_url}
                alt={item.title}
                className="card-img-top"
                style={{ height: 160, objectFit: "cover" }}
              />
            )}
            <div className="card-body d-flex flex-column">
              <div className="d-flex justify-content-between align-items-start">
                <h5 className="card-title mb-1">{item.title}</h5>
                {!item.is_public && (
                  <span className="badge bg-secondary ms-1">Private</span>
                )}
              </div>
              <h6 className="card-subtitle text-muted mb-2 text-capitalize">
                {item.category}
                {item.creator ? ` · ${item.creator}` : ""}
              </h6>

              {item.description && (
                <p className="card-text small flex-grow-1">{item.description}</p>
              )}

              <div className="mb-2">
                {item.tags.map((tag) => (
                  <span key={tag} className="badge bg-light text-dark border tag-pill">
                    {tag}
                  </span>
                ))}
              </div>

              <div className="small text-muted mb-2">
                {item.accession_number && <div>Accession #: {item.accession_number}</div>}
                {item.location && <div>Location: {item.location}</div>}
                {item.condition && (
                  <span className={`badge bg-${CONDITION_BADGE[item.condition] || "secondary"}`}>
                    {item.condition}
                  </span>
                )}
              </div>

              <div className="mt-auto d-flex gap-2">
                <button className="btn btn-sm btn-outline-primary" onClick={() => onEdit(item)}>
                  Edit
                </button>
                <button className="btn btn-sm btn-outline-danger" onClick={() => onDelete(item)}>
                  Delete
                </button>
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
