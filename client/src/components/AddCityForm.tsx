'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function AddCityForm() {
  const [city, setCity] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!city.trim() || loading) return;

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await fetch('/api/add-city', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ city: city.trim() }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to add city.');
      }

      setSuccess(`Successfully added "${city.trim()}"!`);
      setCity('');
      
      // Refresh the page data from the server so the new city shows up
      router.refresh();
      
      // Auto-clear success message after 5 seconds
      setTimeout(() => setSuccess(null), 5000);
    } catch (err: any) {
      console.error(err);
      setError(err.message || 'An unexpected error occurred.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-6xl mx-auto mb-10 p-6 rounded-2xl bg-[var(--card)] border border-[var(--muted-border)] shadow-md transition-all duration-300">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="max-w-md">
          <h3 className="text-lg font-bold text-[var(--foreground)] mb-1 flex items-center gap-2">
            <span>🤖</span> Add New Destination
          </h3>
          <p className="text-xs text-[var(--muted)]">
            Enter a city name (e.g. "London", "Tokyo"). Our autonomous AI Agent will scrape Wikipedia and populate nearby points of interest.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-3 flex-grow max-w-xl w-full">
          <div className="relative flex-grow">
            <input
              type="text"
              value={city}
              onChange={(e) => setCity(e.target.value)}
              disabled={loading}
              placeholder="e.g. San Francisco, Kyoto, Berlin..."
              className="w-full px-4 py-3 rounded-xl border border-[var(--muted-border)] bg-[var(--background)] text-[var(--foreground)] placeholder:text-[var(--muted)]/50 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all text-sm disabled:opacity-50"
            />
            {loading && (
              <span className="absolute right-4 top-1/2 -translate-y-1/2 flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-blue-500"></span>
              </span>
            )}
          </div>
          <button
            type="submit"
            disabled={loading || !city.trim()}
            className="px-6 py-3 rounded-xl bg-gradient-to-r from-blue-500 to-indigo-500 text-white font-semibold text-sm hover:from-blue-600 hover:to-indigo-600 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 active:scale-[0.98] transition-all disabled:opacity-50 disabled:pointer-events-none flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <svg className="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                <span>Researching...</span>
              </>
            ) : (
              <span>Add Destination</span>
            )}
          </button>
        </form>
      </div>

      {/* Status Messages */}
      {loading && (
        <div className="mt-4 p-3 rounded-xl bg-blue-500/5 border border-blue-500/10 text-xs text-blue-500 flex items-center gap-2 animate-pulse">
          <span>⚙️</span>
          <span>The AI Travel Agent is running. Resolving coordinates and analyzing nearby Wikipedia articles for "{city}"... (this takes 10-15s)</span>
        </div>
      )}

      {error && (
        <div className="mt-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-xs text-rose-500 flex items-center gap-2">
          <span>❌</span>
          <span>{error}</span>
        </div>
      )}

      {success && (
        <div className="mt-4 p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-xs text-emerald-500 flex items-center gap-2">
          <span>✅</span>
          <span>{success}</span>
        </div>
      )}
    </div>
  );
}
