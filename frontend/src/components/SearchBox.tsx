import { useEffect, useRef, useState } from "react";
import { api } from "../api";
import type { SearchResult } from "../types";

export function SearchBox({
  onPick,
  disabled,
}: {
  onPick: (symbol: string) => void;
  disabled?: boolean;
}) {
  const [q, setQ] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const boxRef = useRef<HTMLDivElement>(null);

  // Debounced search as the user types.
  useEffect(() => {
    const term = q.trim();
    if (term.length < 2) {
      setResults([]);
      setLoading(false);
      return;
    }
    setLoading(true);
    const id = setTimeout(async () => {
      try {
        const r = await api.search(term);
        setResults(r);
        setOpen(true);
      } catch {
        setResults([]);
      } finally {
        setLoading(false);
      }
    }, 300);
    return () => clearTimeout(id);
  }, [q]);

  // Close the dropdown on outside click.
  useEffect(() => {
    function onDoc(e: MouseEvent) {
      if (boxRef.current && !boxRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", onDoc);
    return () => document.removeEventListener("mousedown", onDoc);
  }, []);

  function pick(symbol: string) {
    setQ("");
    setResults([]);
    setOpen(false);
    onPick(symbol);
  }

  return (
    <div className="search" ref={boxRef}>
      <input
        placeholder="Search company or symbol — e.g. Apple, Reliance, Tata, BTC"
        value={q}
        onChange={(e) => setQ(e.target.value)}
        onFocus={() => results.length > 0 && setOpen(true)}
        onKeyDown={(e) => {
          if (e.key === "Enter" && q.trim()) pick(q.trim().toUpperCase());
          if (e.key === "Escape") setOpen(false);
        }}
        disabled={disabled}
      />
      {open && (loading || results.length > 0) && (
        <ul className="suggest">
          {loading && <li className="muted">Searching…</li>}
          {!loading &&
            results.map((r) => (
              <li key={r.symbol} onMouseDown={() => pick(r.symbol)}>
                <span className="sym">{r.symbol}</span>
                <span className="nm">{r.name}</span>
                <span className="ex">{r.exchange}</span>
              </li>
            ))}
        </ul>
      )}
    </div>
  );
}
