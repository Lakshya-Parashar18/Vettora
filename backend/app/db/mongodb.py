from typing import Optional
from bson import ObjectId
from fastapi import HTTPException
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import PyMongoError, ServerSelectionTimeoutError

from app.config import settings

_mongo_client: Optional[MongoClient] = None


def get_mongo_client() -> Optional[MongoClient]:
    return _mongo_client


def connect_to_mongo() -> None:
    global _mongo_client
    if not settings.mongodb_uri:
        return

    try:
        _mongo_client = MongoClient(
            settings.mongodb_uri,
            serverSelectionTimeoutMS=2000,
            connectTimeoutMS=2000,
        )
        init_db_indexes()
    except Exception:
        pass


def close_mongo_connection() -> None:
    global _mongo_client
    if _mongo_client is not None:
        try:
            _mongo_client.close()
        except Exception:
            pass
        _mongo_client = None


def get_database() -> Optional[Database]:
    client = get_mongo_client()
    if client is None or not settings.mongodb_uri:
        return None
    db_name = settings.mongodb_database or "vettora"
    return client[db_name]


def get_collection(name: str):
    db = get_database()
    if db is None:
        return None
    return db[name]


def get_resumes_collection():
    return get_collection("resumes")


def get_jobs_collection():
    return get_collection("jobs")


def get_evaluations_collection():
    return get_collection("evaluations")


def init_db_indexes() -> None:
    db = get_database()
    if db is None:
        return

    try:
        db["resumes"].create_index("created_at")
        db["jobs"].create_index("created_at")
        db["evaluations"].create_index(
            [("job_id", 1), ("resume_id", 1)],
            unique=True,
            name="job_resume_unique_idx",
        )
        db["evaluations"].create_index(
            [("job_id", 1), ("score", -1)],
            name="job_score_idx",
        )
    except Exception:
        pass


def check_db_health() -> str:
    client = get_mongo_client()
    if client is None or not settings.mongodb_uri:
        return "disconnected"
    try:
        client.admin.command("ping")
        return "connected"
    except (ServerSelectionTimeoutError, PyMongoError, Exception):
        return "disconnected"


def parse_object_id(id_str: str) -> ObjectId:
    if not id_str or not isinstance(id_str, str) or not ObjectId.is_valid(id_str):
        exc = HTTPException(
            status_code=400,
            detail=f"Invalid ID format: {id_str}",
        )
        setattr(exc, "error_code", "invalid_id")
        raise exc
    return ObjectId(id_str)
