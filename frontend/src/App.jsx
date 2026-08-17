import { useEffect, useState, useCallback } from "react";
import SearchBar from "./components/SearchBar.jsx";
import ItemList from "./components/ItemList.jsx";
import ItemForm from "./components/ItemForm.jsx";
import ImportCSV from "./components/ImportCSV.jsx";
import { getItems, createItem, updateItem, deleteItem, uploadItemImage, validateCatalog } from "./api";

export default function App() {
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [filters, setFilters] = useState({ q: "", category: "", condition: "" });
  const [editingItem, setEditingItem] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [validation, setValidation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);

  const loadItems = useCallback(async () => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const params = {};
      if (filters.q) params.q = filters.q;
      if (filters.category) params.category = filters.category;
      if (filters.condition) params.condition = filters.condition;

      const { data } = await getItems(params);
      setItems(data.items);
      setTotal(data.total);
    } catch (err) {
      setErrorMsg("Could not reach the API. Is the Flask backend running on port 5000?");
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    const t = setTimeout(loadItems, 250); // debounce keyword typing
    return () => clearTimeout(t);
  }, [loadItems]);

  const openNewItem = () => {
    setEditingItem(null);
    setShowForm(true);
  };

  const openEditItem = (item) => {
    setEditingItem(item);
    setShowForm(true);
  };

  const handleSave = async (data, imageFile) => {
    let savedItem;
    if (editingItem) {
      const { data: updated } = await updateItem(editingItem.id, data);
      savedItem = updated;
    } else {
      const { data: created } = await createItem(data);
      savedItem = created;
    }

    if (imageFile) {
      await uploadItemImage(savedItem.id, imageFile);
    }

    setShowForm(false);
    loadItems();
  };

  const handleDelete = async (item) => {
    if (!window.confirm(`Delete "${item.title}"? This cannot be undone.`)) return;
    await deleteItem(item.id);
    loadItems();
  };

  const runValidation = async () => {
    const { data } = await validateCatalog();
    setValidation(data);
  };

  return (
    <div>
      <nav className="navbar navbar-dark bg-dark mb-4">
        <div className="container">
          <span className="navbar-brand mb-0 h1">📚 Digital Collections Manager</span>
          <button className="btn btn-light" onClick={openNewItem}>
            + Add Item
          </button>
        </div>
      </nav>

      <div className="container pb-5">
        {errorMsg && <div className="alert alert-danger">{errorMsg}</div>}

        <ImportCSV onImported={loadItems} />

        <div className="d-flex justify-content-between align-items-center mb-2">
          <SearchBar filters={filters} onChange={setFilters} />
        </div>

        <div className="d-flex justify-content-between align-items-center mb-3">
          <span className="text-muted">
            {loading ? "Loading..." : `${total} item${total === 1 ? "" : "s"} found`}
          </span>
          <button className="btn btn-sm btn-outline-dark" onClick={runValidation}>
            Run Data Validation
          </button>
        </div>

        {validation && (
          <div className={`alert ${validation.record_issues.length ? "alert-warning" : "alert-success"}`}>
            <strong>{validation.total_records}</strong> total records scanned.{" "}
            {validation.record_issues.length === 0 && validation.duplicate_accession_numbers.length === 0
              ? "No issues found."
              : `${validation.record_issues.length} record(s) with issues, ${validation.duplicate_accession_numbers.length} duplicate accession number(s).`}
            {validation.record_issues.length > 0 && (
              <ul className="mb-0 mt-2 small">
                {validation.record_issues.map((issue) => (
                  <li key={issue.id}>
                    {issue.title || "(untitled)"}: {issue.problems.join(", ")}
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}

        <ItemList items={items} onEdit={openEditItem} onDelete={handleDelete} />
      </div>

      {showForm && (
        <ItemForm item={editingItem} onSave={handleSave} onCancel={() => setShowForm(false)} />
      )}
    </div>
  );
}
