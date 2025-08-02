import React from 'react';

export default function JobCard({ job, onEdit, onDelete }) {
  return (
    <div className="job-card">
      <h3>{job.title}</h3>
      <small>{job.company} | {job.location} | {job.job_type}</small><br />
      <small>Posted: {new Date(job.posting_date).toLocaleDateString()}</small><br />
      <div>
        {job.tags.map((tag, i) => <span key={i} style={{marginRight: 5, padding: '2px 6px', background: '#ddd', borderRadius: 5}}>{tag}</span>)}
      </div>
      <div style={{ marginTop: 10 }}>
        <button onClick={onEdit}>Edit</button>
        <button onClick={onDelete} style={{ marginLeft: 10 }}>Delete</button>
      </div>
    </div>
  );
}
