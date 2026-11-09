import { useCallback, useRef, useState } from "react";
import { UploadCloud, FileWarning, Download } from "lucide-react";
import Topbar from "../components/Topbar";
import LoadingState from "../components/LoadingState";
import ErrorBanner from "../components/ErrorBanner";
import ScanResultPanel from "../components/ScanResultPanel";
import { scanFile } from "../api/client";

function downloadSample(kind) {
  let blob, filename;
  if (kind === "safe") {
    blob = new Blob(
      ["Team notes: Q3 roadmap draft.\nNothing sensitive here, just a plain text file for testing CyberShield AI."],
      { type: "text/plain" }
    );
    filename = "meeting_notes.txt";
  } else {
    // Fake executable disguised with a double extension + MZ header,
    // for demonstrating the file analyzer's disguise-detection — harmless bytes only.
    const bytes = new Uint8Array(256);
    bytes.set([0x4d, 0x5a]); // "MZ" header, same signature real Windows executables start with
    blob = new Blob([bytes], { type: "application/octet-stream" });
    filename = "invoice_payment.pdf.exe";
  }
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

export default function FileAnalyzer() {
  const [file, setFile] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const inputRef = useRef(null);

  const onDrop = useCallback((e) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files?.[0]) setFile(e.dataTransfer.files[0]);
  }, []);

  async function handleScan() {
    if (!file) {
      setError("Please choose a file to scan.");
      return;
    }
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await scanFile(file);
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex-1 flex flex-col">
      <Topbar title="File Analyzer" subtitle="Upload a file to check for malware, disguise tricks, and embedded threats." />
      <div className="flex-1 px-5 md:px-8 py-6 space-y-6 max-w-3xl w-full">
        <div
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={onDrop}
          onClick={() => inputRef.current?.click()}
          className={`panel cursor-pointer border-dashed p-10 flex flex-col items-center justify-center text-center gap-2 transition-colors ${
            dragOver ? "border-signal bg-signal/5" : ""
          }`}
        >
          <UploadCloud className="h-8 w-8 text-signal" strokeWidth={1.6} />
          <p className="text-sm text-ash-200 font-medium">
            {file ? file.name : "Drag & drop a file here, or click to browse"}
          </p>
          <p className="text-xs text-ash-400">Max 10MB · any file type accepted for analysis</p>
          <input
            ref={inputRef}
            type="file"
            className="hidden"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
          />
        </div>

        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
          <button
            onClick={handleScan}
            disabled={loading}
            className="inline-flex items-center justify-center gap-2 rounded-md bg-signal px-5 py-2.5 text-sm font-medium text-ink hover:bg-signal-soft transition-colors disabled:opacity-60"
          >
            <FileWarning className="h-4 w-4" />
            {loading ? "Scanning…" : "Scan File"}
          </button>
          <div className="flex items-center gap-2 text-xs text-ash-400">
            <span>No file handy? Try a demo sample:</span>
            <button
              onClick={() => downloadSample("safe")}
              className="inline-flex items-center gap-1 rounded-full border border-ink-border px-2.5 py-1 hover:border-signal/40 hover:text-signal transition-colors"
            >
              <Download className="h-3 w-3" /> Safe file
            </button>
            <button
              onClick={() => downloadSample("malicious")}
              className="inline-flex items-center gap-1 rounded-full border border-ink-border px-2.5 py-1 hover:border-verdict-malicious/50 hover:text-verdict-malicious transition-colors"
            >
              <Download className="h-3 w-3" /> Disguised file
            </button>
          </div>
        </div>

        <ErrorBanner message={error} />
        {loading && <LoadingState message="Inspecting file signature, entropy, and embedded content…" />}
        {!loading && result && <ScanResultPanel result={result} />}
      </div>
    </div>
  );
}
