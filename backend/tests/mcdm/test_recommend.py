"""Contract tests for recommend() conforming to contracts/engine_interface.md."""
from app.mcdm.recommend import recommend
from app.schemas.recommend import RecommendRequest, RecommendResult


def test_recommend_contract_matches_engine_interface(
    sample_recommend_request: RecommendRequest,
    sample_stations: list,
    sample_vehicles: dict,
) -> None:
    """Verify recommend() produces schema-compliant RecommendResult."""
    veh = sample_vehicles["E4W"]

    result = recommend(
        request=sample_recommend_request,
        stations=sample_stations,
        vehicle=veh,
    )

    # Assert schema types
    assert isinstance(result, RecommendResult)
    assert isinstance(result.needs_charging, bool)
    assert isinstance(result.reachable_km, float)
    assert len(result.top3) <= 3
    assert len(result.top3) >= 1

    # Check top candidate structure
    top = result.top3[0]
    assert top.rank == 1
    assert 0.0 <= top.score <= 1.0
    assert top.eta_extra_min >= 0.0
    assert top.est_cost_inr >= 0.0
    assert top.est_charge_min >= 0.0
    assert top.criteria.detour_km >= 0.0
    assert top.criteria.cost_inr_kwh > 0.0
    assert len(top.explain) > 0
    assert top.source in ["osm", "ocm", "census", "fixture"]

    # Verify rejected stations list
    rejected_ids = [r.station_id for r in result.rejected]
    assert 4 in rejected_ids  # Station 4 is unoperational
    assert result.engine_version == "0.2.0-mcdm"


def test_recommend_across_six_modes(
    sample_recommend_request: RecommendRequest,
    sample_stations: list,
    sample_vehicles: dict,
) -> None:
    """Verify recommend() runs successfully across all 6 decision modes."""
    modes = ["Cheapest", "Fastest", "Shortest", "HighestRated", "BatterySafe", "Balanced"]
    veh = sample_vehicles["E4W"]

    for m in modes:
        req = sample_recommend_request.model_copy(update={"mode": m})
        res = recommend(request=req, stations=sample_stations, vehicle=veh)
        assert len(res.top3) >= 1
        assert res.top3[0].score >= 0.0


def test_recommend_across_all_four_segments(
    sample_recommend_request: RecommendRequest,
    sample_stations: list,
    sample_vehicles: dict,
) -> None:
    """Verify recommend() functions across E2W, E3W, E4W, ELCV."""
    segments = ["E2W", "E3W", "E4W", "ELCV"]

    for seg in segments:
        veh = sample_vehicles[seg]
        req = sample_recommend_request.model_copy(update={"segment": seg})
        res = recommend(request=req, stations=sample_stations, vehicle=veh)
        assert isinstance(res, RecommendResult)
        assert res.reachable_km > 0.0


def test_recommend_deterministic_reproducibility(
    sample_recommend_request: RecommendRequest,
    sample_stations: list,
    sample_vehicles: dict,
) -> None:
    """Verify that multiple runs with identical input produce identical output."""
    veh = sample_vehicles["E4W"]
    res1 = recommend(sample_recommend_request, sample_stations, veh)
    res2 = recommend(sample_recommend_request, sample_stations, veh)

    assert res1.top3[0].station_id == res2.top3[0].station_id
    assert res1.top3[0].score == res2.top3[0].score
    assert len(res1.rejected) == len(res2.rejected)
