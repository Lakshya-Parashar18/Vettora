from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from bson import ObjectId
from fastapi import HTTPException
from fastapi.testclient import TestClient
import pytest

from app.db.mongodb import check_db_health, parse_object_id
from app.main import app
from app.schemas.job import JobDescription
from app.schemas.resume import ResumeCandidate, ResumeMetadata, ResumeUploadItem, StructuredResume
from app.schemas.evaluation import ScoreBreakdown, CandidateEvaluation, SemanticEvaluation

client = TestClient(app)


def test_1_mongodb_connection_configuration():
    with patch("app.db.mongodb.get_mongo_client") as mock_get_client:
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.admin.command.return_value = {"ok": 1}
        assert check_db_health() == "connected"

    with patch("app.db.mongodb.get_mongo_client", return_value=None):
        assert check_db_health() == "disconnected"


def test_2_resume_insertion_and_5_retrieval():
    resumes_data = {}

    def mock_insert_one(doc):
        obj_id = ObjectId()
        doc["_id"] = obj_id
        resumes_data[obj_id] = doc
        res = MagicMock()
        res.inserted_id = obj_id
        return res

    def mock_find_one(query):
        return resumes_data.get(query.get("_id"))

    mock_col = MagicMock()
    mock_col.insert_one.side_effect = mock_insert_one
    mock_col.find_one.side_effect = mock_find_one

    with patch("app.api.routes.resumes.get_resumes_collection", return_value=mock_col), \
         patch("app.api.routes.resumes.parse_resume_file") as mock_parse:

        mock_resume = StructuredResume(
            candidate=ResumeCandidate(name="John Doe", email="john@example.com", phone="123-456-7890"),
            skills=["Python", "FastAPI", "MongoDB"],
            education=[],
            experience=[],
            projects=[],
            certifications=[],
            metadata=ResumeMetadata(extraction_method="native", llm_structured=True),
        )
        item = ResumeUploadItem(
            filename="john_doe.pdf",
            status="processed",
            extraction_method="native",
            candidate=mock_resume.candidate,
            resume=mock_resume,
            raw_text="John Doe resume content",
        )
        mock_parse.return_value = item


        response = client.post(
            "/resumes/upload",
            files=[("files", ("john_doe.pdf", b"pdf content", "application/pdf"))],
        )

        assert response.status_code == 200
        data = response.json()
        assert "resumes" in data
        assert len(data["resumes"]) == 1
        uploaded = data["resumes"][0]
        assert uploaded["status"] == "processed"
        assert uploaded["resume_id"] is not None
        assert uploaded.get("raw_text") is None

        inserted_id = uploaded["resume_id"]

        get_res = client.get(f"/resumes/{inserted_id}")
        assert get_res.status_code == 200
        get_data = get_res.json()
        assert get_data["resume_id"] == inserted_id
        assert get_data["resume"]["candidate"]["name"] == "John Doe"


def test_3_job_insertion_and_6_retrieval():
    jobs_data = {}

    def mock_insert_one(doc):
        obj_id = ObjectId()
        doc["_id"] = obj_id
        jobs_data[obj_id] = doc
        res = MagicMock()
        res.inserted_id = obj_id
        return res

    def mock_find_one(query):
        return jobs_data.get(query.get("_id"))

    mock_col = MagicMock()
    mock_col.insert_one.side_effect = mock_insert_one
    mock_col.find_one.side_effect = mock_find_one

    mock_jd = JobDescription(
        title="Senior Python Engineer",
        required_skills=["Python", "FastAPI"],
        preferred_skills=["MongoDB", "Docker"],
    )

    with patch("app.api.routes.jobs.get_jobs_collection", return_value=mock_col), \
         patch("app.api.routes.jobs.extract_job_description_with_llm", return_value=mock_jd):

        response = client.post(
            "/jobs",
            json={"text": "Looking for a Senior Python Engineer with FastAPI and MongoDB skills."},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "processed"
        assert data["job_id"] is not None
        job_id = data["job_id"]

        get_res = client.get(f"/jobs/{job_id}")
        assert get_res.status_code == 200
        get_data = get_res.json()
        assert get_data["job_id"] == job_id
        assert get_data["job"]["title"] == "Senior Python Engineer"


def test_4_evaluation_insertion_and_7_retrieval():
    evals_data = {}

    def mock_insert_one(doc):
        obj_id = ObjectId()
        doc["_id"] = obj_id
        evals_data[obj_id] = doc
        res = MagicMock()
        res.inserted_id = obj_id
        return res

    def mock_find_one(query):
        if "_id" in query:
            return evals_data.get(query["_id"])
        return None

    mock_evals_col = MagicMock()
    mock_evals_col.insert_one.side_effect = mock_insert_one
    mock_evals_col.find_one.side_effect = mock_find_one

    eval_obj_id = ObjectId()
    job_obj_id = ObjectId()
    resume_obj_id = ObjectId()

    eval_doc = {
        "_id": eval_obj_id,
        "job_id": job_obj_id,
        "resume_id": resume_obj_id,
        "candidate": {"name": "Alice Smith", "email": "alice@example.com"},
        "score": 8.7,
        "recommendation": "Strong Match",
        "score_breakdown": {
            "skills": 85.0,
            "experience": 100.0,
            "education": 100.0,
            "required_criteria": 75.0,
            "semantic_fit": 88.0,
        },
        "matched_required_skills": ["Python"],
        "missing_required_skills": [],
        "matched_preferred_skills": ["MongoDB"],
        "missing_preferred_skills": [],
        "strengths": ["Strong python background"],
        "concerns": [],
        "justification": "Candidate meets core requirements.",
        "evidence": [],
        "created_at": datetime.now(timezone.utc),
    }
    evals_data[eval_obj_id] = eval_doc

    with patch("app.api.routes.screening.get_evaluations_collection", return_value=mock_evals_col):
        response = client.get(f"/evaluations/{str(eval_obj_id)}")
        assert response.status_code == 200
        data = response.json()
        assert data["evaluation_id"] == str(eval_obj_id)
        assert data["score"] == 8.7
        assert data["recommendation"] == "Strong Match"
        assert data["candidate"]["name"] == "Alice Smith"


def test_8_invalid_object_id():
    with pytest.raises(HTTPException) as exc_info:
        parse_object_id("invalid-hex-id-123")
    assert exc_info.value.status_code == 400

    response = client.get("/resumes/invalid-id-xyz")
    assert response.status_code == 400
    assert response.json()["error"] == "invalid_id"

    response = client.get("/jobs/invalid-id-xyz")
    assert response.status_code == 400
    assert response.json()["error"] == "invalid_id"

    response = client.get("/evaluations/invalid-id-xyz")
    assert response.status_code == 400
    assert response.json()["error"] == "invalid_id"


def test_9_missing_resume_and_10_missing_job():
    valid_obj_id = str(ObjectId())

    mock_col = MagicMock()
    mock_col.find_one.return_value = None

    with patch("app.api.routes.resumes.get_resumes_collection", return_value=mock_col):
        res = client.get(f"/resumes/{valid_obj_id}")
        assert res.status_code == 404
        assert res.json()["error"] == "resume_not_found"

    with patch("app.api.routes.jobs.get_jobs_collection", return_value=mock_col):
        res = client.get(f"/jobs/{valid_obj_id}")
        assert res.status_code == 404
        assert res.json()["error"] == "job_not_found"


def test_11_duplicate_evaluation_handling_and_12_13_14_15_screening_flow():
    jobs_db = {}
    resumes_db = {}
    evals_db = {}

    job_id_obj = ObjectId()
    job_id_str = str(job_id_obj)

    jobs_db[job_id_obj] = {
        "_id": job_id_obj,
        "raw_text": "Python Developer needed",
        "job": {
            "title": "Python Developer",
            "required_skills": ["Python"],
            "preferred_skills": ["MongoDB"],
            "experience": {"minimum_years": 2, "maximum_years": None},
            "education": {"required": False, "degrees": [], "fields": []},
            "responsibilities": [],
            "preferred_qualifications": [],
            "location": None,
            "employment_type": None,
        },
        "created_at": datetime.now(timezone.utc),
    }

    r1_obj = ObjectId()
    r1_str = str(r1_obj)
    resumes_db[r1_obj] = {
        "_id": r1_obj,
        "filename": "cand1.pdf",
        "resume": {
            "candidate": {"name": "Alice Candidate", "email": "alice@test.com", "phone": "111"},
            "skills": ["Python", "MongoDB"],
            "education": [],
            "experience": [],
            "projects": [],
            "certifications": [],
            "metadata": {"extraction_method": "native", "llm_structured": True},
        },
    }

    r2_obj = ObjectId()
    r2_str = str(r2_obj)
    resumes_db[r2_obj] = {
        "_id": r2_obj,
        "filename": "cand2.pdf",
        "resume": {
            "candidate": {"name": "Bob Candidate", "email": "bob@test.com", "phone": "222"},
            "skills": ["Python"],
            "education": [],
            "experience": [],
            "projects": [],
            "certifications": [],
            "metadata": {"extraction_method": "native", "llm_structured": True},
        },
    }

    r3_missing_str = str(ObjectId())

    mock_jobs_col = MagicMock()
    mock_jobs_col.find_one.side_effect = lambda q: jobs_db.get(q.get("_id"))

    mock_resumes_col = MagicMock()
    mock_resumes_col.find_one.side_effect = lambda q: resumes_db.get(q.get("_id"))

    def mock_eval_find_one(query):
        for doc in evals_db.values():
            if doc.get("job_id") == query.get("job_id") and doc.get("resume_id") == query.get("resume_id"):
                return doc
        return None

    def mock_eval_insert_one(doc):
        new_id = ObjectId()
        doc["_id"] = new_id
        evals_db[new_id] = doc
        res = MagicMock()
        res.inserted_id = new_id
        return res

    def mock_eval_update_one(query, update):
        target_id = query.get("_id")
        if target_id in evals_db:
            evals_db[target_id].update(update.get("$set", {}))

    def mock_eval_find(query):
        results = [doc for doc in evals_db.values() if doc.get("job_id") == query.get("job_id")]
        return results

    mock_evals_col = MagicMock()
    mock_evals_col.find_one.side_effect = mock_eval_find_one
    mock_evals_col.insert_one.side_effect = mock_eval_insert_one
    mock_evals_col.update_one.side_effect = mock_eval_update_one
    mock_evals_col.find.side_effect = mock_eval_find

    mock_sem_fit = SemanticEvaluation(
        semantic_score=85.0,
        matched_requirements=["Python"],
        semantic_strengths=["Strong skills"],
        semantic_concerns=[],
        evidence=[],
        justification="Fits job profile well.",
    )

    with patch("app.api.routes.screening.get_jobs_collection", return_value=mock_jobs_col), \
         patch("app.api.routes.screening.get_resumes_collection", return_value=mock_resumes_col), \
         patch("app.api.routes.screening.get_evaluations_collection", return_value=mock_evals_col), \
         patch("app.api.routes.screening.evaluate_semantic_fit_with_llm", return_value=mock_sem_fit):

        screen_payload = {
            "job_id": job_id_str,
            "resume_ids": [r1_str, r2_str, r3_missing_str],
        }

        res = client.post("/screen", json=screen_payload)
        assert res.status_code == 200
        data = res.json()
        assert data["job_id"] == job_id_str
        cands = data["candidates"]
        assert len(cands) == 3

        processed = [c for c in cands if c["status"] == "processed"]
        failed = [c for c in cands if c["status"] == "failed"]
        assert len(processed) == 2
        assert len(failed) == 1
        assert failed[0]["resume_id"] == r3_missing_str

        assert processed[0]["score"] >= processed[1]["score"]

        res_repeat = client.post("/screen", json=screen_payload)
        assert res_repeat.status_code == 200
        assert len(evals_db) == 2

        cand_list_res = client.get(f"/candidates/{job_id_str}")
        assert cand_list_res.status_code == 200
        cand_list_data = cand_list_res.json()
        assert len(cand_list_data["candidates"]) == 2
        assert cand_list_data["candidates"][0]["score"] >= cand_list_data["candidates"][1]["score"]


def test_16_health_endpoint_with_database_status():
    with patch("app.api.routes.health.check_db_health", return_value="connected"):
        res = client.get("/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "ok"
        assert data["service"] == "vettora-api"
        assert data["database"] == "connected"

    with patch("app.api.routes.health.check_db_health", return_value="disconnected"):
        res = client.get("/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "ok"
        assert data["database"] == "disconnected"
