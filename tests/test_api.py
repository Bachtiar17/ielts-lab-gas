"""FastAPI integration tests & seed content integrity verification (Milestones 1 & 2)."""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.db.session import Base, get_db
from backend.app.main import create_app
from backend.app.seeds.listening_seed import LISTENING_PARTS, LISTENING_QUESTIONS, LISTENING_TEST_ID
from backend.app.seeds.reading_bank_p1 import P1_DRILLS
from backend.app.seeds.reading_bank_p2 import P2_DRILLS
from backend.app.seeds.reading_bank_p3 import P3_DRILLS
from backend.app.seeds.reading_seed import PASSAGES, QUESTIONS, READING_TEST_ID, run_all_seeds


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    Base.metadata.create_all(bind=engine)
    with TestingSessionLocal() as db:
        run_all_seeds(db)

    app = create_app()

    def override_get_db() -> Generator[Session, None, None]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client


def test_seed_has_40_mock_questions_and_30_reading_drills_all_verbatim() -> None:
    assert len(PASSAGES) == 3
    assert len(QUESTIONS) == 40
    assert [q["question_number"] for q in QUESTIONS] == list(range(1, 41))

    para_lookup: dict[tuple[int, str], str] = {}
    for passage in PASSAGES:
        for para in passage["paragraphs"]:
            para_lookup[(passage["index"], para["id"])] = para["text"]

    for q in QUESTIONS:
        ev = q["evidence_span"]
        key = (q["passage_index"], ev["paragraph_id"])
        assert ev["quote"] in para_lookup[key], f"Mock Q{q['question_number']} quote mismatch"

    all_drills = P1_DRILLS + P2_DRILLS + P3_DRILLS
    assert len(all_drills) == 30
    assert len({d["id"] for d in all_drills}) == 30

    for drill in all_drills:
        p0 = drill["passages"][0]
        pmap = {p["id"]: p["text"] for p in p0["paragraphs"]}
        assert len(drill["questions"]) == 6
        for q in drill["questions"]:
            ev = q["evidence_span"]
            assert ev["paragraph_id"] in pmap, f"{drill['id']} Q{q['question_number']} missing para"
            assert ev["quote"] in pmap[ev["paragraph_id"]], (
                f"{drill['id']} Q{q['question_number']} quote not verbatim in Para {ev['paragraph_id']}"
            )


def test_listening_seed_has_40_questions_and_valid_transcript_evidence() -> None:
    assert len(LISTENING_PARTS) == 4
    assert len(LISTENING_QUESTIONS) == 40
    assert [q["question_number"] for q in LISTENING_QUESTIONS] == list(range(1, 41))

    turns_by_part: dict[int, dict[str, str]] = {}
    for part in LISTENING_PARTS:
        turns_by_part[part["index"]] = {t["id"]: t["text"] for t in part["transcript"]}

    for q in LISTENING_QUESTIONS:
        ev = q["evidence_span"]
        part_turns = turns_by_part[q["passage_index"]]
        assert ev["transcript_id"] in part_turns, f"Listening Q{q['question_number']} missing transcript_id"
        # First segment before any ellipsis must exist in the transcript turn
        core_quote = ev["quote"].split("...")[0].strip()
        assert core_quote in part_turns[ev["transcript_id"]], (
            f"Listening Q{q['question_number']} quote not found in {ev['transcript_id']}"
        )


def test_reading_drills_rotation_past_session_review_and_reset(client: TestClient) -> None:
    health = client.get("/api/health").json()
    assert health["reading_drill_bank_count"] == 30
    assert health["listening_test_count"] == 1

    # Rotating 30-passage drill picker returns 3 distinct slots (1, 2, 3) and respects exclude
    r1 = client.get("/api/reading/drills/random").json()
    assert r1["bank_size"] == 30
    assert [d["drill_slot"] for d in r1["drills"]] == [1, 2, 3]
    ids1 = [d["id"] for d in r1["drills"]]

    r2 = client.get(f"/api/reading/drills/random?exclude={','.join(ids1)}").json()
    ids2 = [d["id"] for d in r2["drills"]]
    assert set(ids1).isdisjoint(set(ids2))

    # Run a drill from the 30-passage bank
    drill_id = ids1[0]
    detail = client.get(f"/api/reading/tests/{drill_id}").json()
    assert len(detail["questions"]) == 6
    for q in detail["questions"]:
        assert "answer_key" not in q

    sess_id = client.post(
        "/api/reading/sessions",
        json={"test_id": drill_id, "mode": "drill"},
    ).json()["session_id"]

    submitted = client.post(
        f"/api/reading/sessions/{sess_id}/submit",
        json={"answers": {detail["questions"][0]["id"]: "TRUE"}, "duration_sec": 95},
    ).json()
    assert submitted["total_questions"] == 6

    # Retrieve completed past session summary by session_id
    review = client.get(f"/api/sessions/{sess_id}")
    assert review.status_code == 200
    rev_json = review.json()
    assert rev_json["session_id"] == sess_id
    assert rev_json["raw_score"] == submitted["raw_score"]
    assert len(rev_json["verdicts"]) == 6

    # Reset skill accuracy profile and recent sessions independently
    del_skills = client.delete("/api/skills").json()
    assert del_skills["deleted_count"] >= 1
    assert client.get("/api/progress").json()["skills"] == []
    assert len(client.get("/api/progress").json()["recent_sessions"]) == 1

    del_sess = client.delete("/api/sessions").json()
    assert del_sess["deleted_count"] == 1
    assert client.get("/api/progress").json()["recent_sessions"] == []


def test_listening_end_to_end_grading_and_review(client: TestClient) -> None:
    tests = client.get("/api/listening/tests").json()
    assert len(tests) == 1
    assert tests[0]["id"] == LISTENING_TEST_ID
    assert tests[0]["total_questions"] == 40
    assert tests[0]["parts"][1]["has_map"] is True

    detail = client.get(f"/api/listening/tests/{LISTENING_TEST_ID}?part_index=1").json()
    assert len(detail["questions"]) == 10
    for q in detail["questions"]:
        assert "answer_key" not in q

    sess_id = client.post(
        "/api/listening/sessions",
        json={"test_id": LISTENING_TEST_ID, "mode": "drill", "passage_index": 1},
    ).json()["session_id"]

    # Mix exact, normalized date/time/currency/postcode, and intentional self-correction mistake
    answers = {
        "l1-q01": "Hargreaves",
        "l1-q02": "bh147qr",        # Postcode without space
        "l1-q03": "45",             # Bare number matching £45
        "l1-q04": "14th",           # Rescheduled date
        "l1-q05": "9.30 am",        # Dot time format
        "l1-q06": "sandals",
        "l1-q07": "sunscreen",
        "l1-q08": "kayaking",
        "l1-q09": "old bakery",     # Intentional word-limit violation (ONE WORD AND/OR A NUMBER)
        "l1-q10": "Claire",         # Intentional distractor mistake (should be Martin)
    }
    res = client.post(
        f"/api/listening/sessions/{sess_id}/submit",
        json={"answers": answers, "duration_sec": 310},
    ).json()
    assert res["module"] == "listening"
    assert res["raw_score"] == 8
    assert res["total_questions"] == 10
    assert res["band_score"] == 7.5  # 8/10 -> 32/40 on Listening curve -> Band 7.5!

    vmap = {v["item_id"]: v for v in res["verdicts"]}
    assert vmap["l1-q09"]["failure_reason"] == "word_limit_exceeded"
    assert vmap["l1-q10"]["failure_reason"] == "incorrect"

    # Past Listening session retrieval
    rev = client.get(f"/api/sessions/{sess_id}").json()
    assert rev["module"] == "listening"
    assert rev["band_score"] == 7.5

    # Listening distractor explanation
    exp = client.post(
        "/api/listening/explain",
        json={"item_id": "l1-q10", "user_answer": "Claire", "failure_reason": "incorrect"},
    ).json()
    assert exp["accepted_answers"] == ["Martin"]
    assert exp["strategy_note"]["question_type"] == "form_note_table_completion"


def test_reading_mock_security_and_grading(client: TestClient) -> None:
    detail = client.get(f"/api/reading/tests/{READING_TEST_ID}?passage_index=1").json()
    assert len(detail["questions"]) == 13
    for q in detail["questions"]:
        assert "answer_key" not in q
        assert "evidence_span" not in q
