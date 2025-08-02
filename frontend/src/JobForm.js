import React, { useEffect, useState } from 'react';

export default function JobForm({ onSubmit, editingJob }) {
  const [form, setForm] = useState({ title: '', company: '', location: '', job_type: '', tags: '' });

  useEffect(() => {
    if (editingJob) {
      setForm({ ...editingJob, tags: editingJob.tags.join(', ') });
    }
  }, [editingJob]);

  const handleChange = e => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = e => {
    e.preventDefault();
    const payload = { ...form, tags: form.tags.split(',').map(tag => tag.trim()) };
    if (editingJob) payload.id = editingJob.id;
    onSubmit(payload);
    setForm({ title: '', company: '', location: '', job_type: '', tags: '' });
  };

  return (
    <form onSubmit={handleSubmit} style={{ marginBottom: 20 }}>
      <input name="title" placeholder="Job Title" value={form.title} onChange={handleChange} required />
      <input name="company" placeholder="Company" value={form.company} onChange={handleChange} required />
      <input name="location" placeholder="Location" value={form.location} onChange={handleChange} required />
      <input name="job_type" placeholder="Job Type" value={form.job_type} onChange={handleChange} />
      <input name="tags" placeholder="Tags (comma-separated)" value={form.tags} onChange={handleChange} />
      <div style={{ height: 12 }} />
      <button type="submit" style={{ marginTop: 10 }}>{editingJob ? 'Update Job' : 'Add Job'}</button>
    </form>
  );
}
