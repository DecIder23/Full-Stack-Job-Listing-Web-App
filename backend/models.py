from datetime import datetime
from backend import db

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    company = db.Column(db.String(120), nullable=False)
    location = db.Column(db.String(120), nullable=False)
    posting_date = db.Column(db.DateTime, default=datetime.utcnow)
    job_type = db.Column(db.String(50), nullable=False)
    tags = db.Column(db.String(300))

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "posting_date": self.posting_date.isoformat(),
            "job_type": self.job_type,
            "tags": self.tags.split(",") if self.tags else []
        }
