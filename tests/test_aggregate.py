"""Agrégation multi-sources : dédoublonnage, fraîcheur, fusion des champs."""

from __future__ import annotations

from sources.aggregate import aggregate, normalize_key


def _rec(external_id, ville="Lyon", ingested_at="2024-01-01", source="s"):
    return {
        "external_id": external_id,
        "raison_sociale": "Acme",
        "ville": ville,
        "ingested_at": ingested_at,
        "source": source,
    }


def test_key_is_case_and_space_insensitive():
    assert normalize_key("  fr-001 ") == normalize_key("FR-001")


def test_exact_duplicates_are_merged():
    out = aggregate([_rec("FR-1"), _rec("FR-1"), _rec("FR-2")])
    assert len(out) == 2


def test_freshest_record_wins():
    out = aggregate(
        [
            _rec("FR-1", ville="Lyon", ingested_at="2024-01-01"),
            _rec("FR-1", ville="Paris", ingested_at="2024-06-01"),
        ]
    )
    assert len(out) == 1
    assert out[0]["ville"] == "Paris"


def test_blank_fields_are_coalesced():
    out = aggregate(
        [
            _rec("FR-1", ville="", ingested_at="2024-06-01"),
            _rec("FR-1", ville="Lyon", ingested_at="2024-01-01"),
        ]
    )
    assert len(out) == 1
    assert out[0]["ville"] == "Lyon"
