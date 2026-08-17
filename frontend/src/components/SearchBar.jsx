export default function SearchBar({ filters, onChange }) {
  const handle = (field) => (e) => onChange({ ...filters, [field]: e.target.value });

  return (
    <div className="row g-2 align-items-center mb-3">
      <div className="col-md-5">
        <input
          type="text"
          className="form-control"
          placeholder="Search by title, creator, tags, accession #..."
          value={filters.q}
          onChange={handle("q")}
        />
      </div>
      <div className="col-md-3">
        <select className="form-select" value={filters.category} onChange={handle("category")}>
          <option value="">All categories</option>
          <option value="book">Book</option>
          <option value="archive">Archive</option>
          <option value="photo">Photo</option>
          <option value="artifact">Artifact</option>
          <option value="other">Other</option>
        </select>
      </div>
      <div className="col-md-3">
        <select className="form-select" value={filters.condition} onChange={handle("condition")}>
          <option value="">Any condition</option>
          <option value="excellent">Excellent</option>
          <option value="good">Good</option>
          <option value="fair">Fair</option>
          <option value="poor">Poor</option>
        </select>
      </div>
      <div className="col-md-1">
        <button
          className="btn btn-outline-secondary w-100"
          onClick={() => onChange({ q: "", category: "", condition: "" })}
          title="Clear filters"
        >
          Clear
        </button>
      </div>
    </div>
  );
}
