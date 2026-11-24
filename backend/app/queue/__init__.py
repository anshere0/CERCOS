"""CERCOS Queue Modeling Package.

Provides Erlang-C (M/M/c) and Allen-Cunneen (M/G/c) wait time estimation models.
"""
from app.queue.queue import (
    allen_cunneen_mgc_wq,
    erlang_c,
    estimate_station_wait_min,
    mmc_wq,
)

__all__ = ["allen_cunneen_mgc_wq", "erlang_c", "estimate_station_wait_min", "mmc_wq"]
