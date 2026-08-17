import { useRef, useState } from "react";
import { importCSV, exportCSVUrl } from "../api";

export default function ImportCSV({ onImported }) {
  const fileInput = useRef(null);
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFile = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setLoading(true);
    setReport(null);
    try {
      const { data } = await importCSV(file);
      setReport(data);
      onImported();
    } catch (err) {
      setReport({ error: err.response?.data?.error || "Import failed." });
    } finally {
      setLoading(false);
      fileInput.current.value = "";
    }
  };

  return (
    <div className="card mb-3">
      <div className="card-body">
        <div className="d-flex align-items-center gap-2 flex-wrap">
          <label className="btn btn-outline-dark mb-0">
            {loading ? "Importing..." : "Bulk Import CSV"}
            <input
              type="file"
              accept=".csv"
              ref={fileInput}
              onChange={handleFile}
              hidden
              disabled={loading}
            />
          </label>
          <a className="btn btn-outline-secondary" href={exportCSVUrl}>
            Export CSV
          </a>
          <span className="text-muted small">
            CSV columns: title, category, creator, donor, accession_number, condition, location, description, tags
          </span>
        </div>

        {report && (
          <div className="mt-3">
            {report.error ? (
              <div className="alert alert-danger mb-0">{report.error}</div>
            ) : (
              <div className={`alert ${report.error_count ? "alert-warning" : "alert-success"} mb-0`}>
                Imported {report.created_count} item(s).
                {report.error_count > 0 && ` ${report.error_count} row(s) had errors:`}
                {report.error_count > 0 && (
                  <ul className="mb-0 mt-1">
                    {report.errors.map((e) => (
                      <li key={e.row}>
                        Row {e.row}: {e.error}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
