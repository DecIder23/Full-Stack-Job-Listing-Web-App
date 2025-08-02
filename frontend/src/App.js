import React, { useEffect, useState } from 'react';
import JobForm from './JobForm';
import JobCard from './JobCard';
import Filters from './Filters';

const API = 'http://localhost:5000/jobs';

function App() {
  const [jobs, setJobs] = useState([]);
  const [filters, setFilters] = useState({});
  const [editingJob, setEditingJob] = useState(null);

  const fetchJobs = async () => {
    const params = new URLSearchParams(filters).toString();
    const res = await fetch(`${API}?${params}`);
    const data = await res.json();
    setJobs(data);
  };

  useEffect(() => {
    fetchJobs();
  }, [filters]);

  const handleAdd = async (job) => {
    await fetch(API, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(job)
    });
    fetchJobs();
  };

  const handleUpdate = async (job) => {
    await fetch(`${API}/${job.id}`, {
      method: 'PATCH',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(job)
    });
    setEditingJob(null);
    fetchJobs();
  };

  const handleDelete = async (id) => {
    await fetch(`${API}/${id}`, { method: 'DELETE' });
    fetchJobs();
  };

  return (
    <div className="container">
      <h1>Job Listings</h1>
      <Filters setFilters={setFilters} />
      <JobForm onSubmit={editingJob ? handleUpdate : handleAdd} editingJob={editingJob} />
      {jobs.map(job => (
        <JobCard
          key={job.id}
          job={job}
          onEdit={() => setEditingJob(job)}
          onDelete={() => handleDelete(job.id)}
        />
      ))}
    </div>
  );
}

export default App;