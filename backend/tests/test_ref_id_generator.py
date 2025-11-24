import pytest
from app.utils.ref_id_generator import generate_ref_id, generate_unique_ref_id


def test_generate_ref_id_format():
    """Test ref_id format"""
    ref_id = generate_ref_id()
    
    assert ref_id.startswith("ACB")
    assert len(ref_id) == 8  # ACB + 5 characters
    assert ref_id[3:].isalnum()
    assert ref_id[3:].isupper()


def test_generate_ref_id_uniqueness():
    """Test that generated ref_ids are unique"""
    ref_ids = {generate_ref_id() for _ in range(1000)}
    
    # Should have high uniqueness (at least 99%)
    assert len(ref_ids) >= 990


def test_generate_unique_ref_id_avoids_collisions():
    """Test that unique ref_id avoids existing IDs"""
    existing_ids = {"ACBABC12", "ACBXYZ99", "ACB12345"}
    
    for _ in range(100):
        ref_id = generate_unique_ref_id(existing_ids)
        assert ref_id not in existing_ids


def test_generate_unique_ref_id_empty_set():
    """Test with empty existing IDs"""
    ref_id = generate_unique_ref_id(set())
    
    assert ref_id.startswith("ACB")
    assert len(ref_id) == 8