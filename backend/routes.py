from flask import Blueprint, request, jsonify
from backend.models import Job
from backend import db
from sqlalchemy import desc, asc

job_routes = Blueprint('job_routes', __name__)

@job_routes.route('/jobs', methods=['GET'])
def get_jobs():
    job_type = request.args.get('job_type')
    location = request.args.get('location')
    tag = request.args.get('tag')
    sort = request.args.get('sort', 'posting_date_desc')

    query = Job.query

    if job_type:
        query = query.filter_by(job_type=job_type)
    if location:
        query = query.filter_by(location=location)
    if tag:
        query = query.filter(Job.tags.like(f"%{tag}%"))

    if sort == 'posting_date_asc':
        query = query.order_by(asc(Job.posting_date))
    else:
        query = query.order_by(desc(Job.posting_date))

    jobs = query.all()
    return jsonify([job.to_dict() for job in jobs])

@job_routes.route('/jobs/<int:job_id>', methods=['GET'])
def get_job(job_id):
    job = Job.query.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    return jsonify(job.to_dict())

@job_routes.route('/jobs', methods=['POST'])
def create_job():
    from datetime import datetime
    data = request.get_json()
    if not data.get("title") or not data.get("company") or not data.get("location"):
        return jsonify({"error": "Missing required fields"}), 400

    # Parse posting_date if it's a string
    posting_date = data.get("posting_date")
    if isinstance(posting_date, str):
        try:
            posting_date = datetime.fromisoformat(posting_date)
        except ValueError:
            posting_date = datetime.utcnow()

    # Accept tags as list or comma-separated string
    tags = data.get("tags", [])
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",") if t.strip()]

    job = Job(
        title=data["title"],
        company=data["company"],
        location=data["location"],
        posting_date=posting_date,
        job_type=data.get("job_type", "Full-time"),
        tags=",".join(tags)
    )
    db.session.add(job)
    db.session.commit()
    return jsonify(job.to_dict()), 201

@job_routes.route('/jobs/<int:job_id>', methods=['PUT', 'PATCH'])
def update_job(job_id):
    job = Job.query.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404

    data = request.get_json()
    for field in ["title", "company", "location", "job_type", "tags"]:
        if field in data:
            setattr(job, field, ",".join(data["tags"]) if field == "tags" else data[field])
    db.session.commit()
    return jsonify(job.to_dict())

@job_routes.route('/jobs/<int:job_id>', methods=['DELETE'])
def delete_job(job_id):
    job = Job.query.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    db.session.delete(job)
    db.session.commit()
    return jsonify({"message": "Job deleted"})
