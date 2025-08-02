import React, { useState } from 'react';

export default function Filters({ setFilters }) {
  const [job_type, setJobType] = useState('');
  const [location, setLocation] = useState('');
  const [tag, setTag] = useState('');
  const [sort, setSort] = useState('posting_date_desc');

  const applyFilters = () => {
    setFilters({ job_type, location, tag, sort });
  };

  return (
    <div style={{ marginBottom: 20, display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: 10 }}>
      <select onChange={e => setJobType(e.target.value)} value={job_type}>
        <option value="">All Types</option>
        <option>Full-time</option>
        <option>Part-time</option>
        <option>Internship</option>
      </select>
      <input placeholder="Location" value={location} onChange={e => setLocation(e.target.value)} />
      <input placeholder="Tag" value={tag} onChange={e => setTag(e.target.value)} />
      <select onChange={e => setSort(e.target.value)} value={sort}>
        <option value="posting_date_desc">Newest First</option>
        <option value="posting_date_asc">Oldest First</option>
      </select>
      <div style={{ flex: 1 }} />
      <button onClick={applyFilters} style={{ marginLeft: 'auto', minWidth: 120 }}>Apply Filters</button>
    </div>
  );
}