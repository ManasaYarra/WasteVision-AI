import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.database import WasteDatabase

def test_database_lifecycle():
    tmp_dir = tempfile.mkdtemp()
    test_db_path = os.path.join(tmp_dir, "test_waste_history.db")
    
    db = WasteDatabase(db_path=test_db_path)
    
    # Save a classification
    rec_id = db.save_classification(
        item_name="PET Plastic Bottle",
        category="Recyclable",
        confidence=0.96,
        explanation="Recyclable plastic container signature",
        disposal_instructions=["Rinse container", "Place in blue bin"],
        co2_saved_kg=0.45
    )
    assert rec_id == 1

    # Fetch history
    history = db.get_history()
    assert len(history) == 1
    assert history[0]["item_name"] == "PET Plastic Bottle"

    # Fetch stats
    stats = db.get_stats()
    assert stats["total_items"] == 1
    assert stats["total_co2_saved_kg"] == 0.45
    assert stats["category_counts"]["Recyclable"] == 1

    # Clear history
    db.clear_history()
    assert len(db.get_history()) == 0

    # Test Public Waste Reports DB logic
    ref_id = db.save_public_report(
        item_name="Overflowing Battery Waste Dump",
        category="Hazardous",
        confidence=0.95,
        urgency="🔴 High Priority",
        priority_rank=1,
        location="5th Avenue Park Gate",
        notes="Hazardous batteries leaking on sidewalk"
    )
    assert ref_id.startswith("#WV-")

    reports = db.get_public_reports()
    assert len(reports) == 1
    assert reports[0]["ref_id"] == ref_id
    assert reports[0]["status"] == "New"

    # Update status
    db.update_report_status(reports[0]["id"], "In Progress")
    updated_reports = db.get_public_reports()
    assert updated_reports[0]["status"] == "In Progress"

    pub_stats = db.get_public_reports_stats()
    assert pub_stats["total"] == 1
    assert pub_stats["in_progress"] == 1

    print("[SUCCESS] Database lifecycle & public reports tests passed!")

if __name__ == "__main__":
    test_database_lifecycle()
