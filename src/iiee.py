"""IIEE decomposition functions for sea ice forecast validation.

Implements the Integrated Ice Edge Error (IIEE) and its decomposition
into Absolute Extent Error (AEE) and Misplacement Error (ME) following
Goessling et al. (2016).

Reference:
    Goessling, H.F., et al. (2016). Predictability of the Arctic sea ice edge.
    Geophysical Research Letters, 43(4), 1642-1650.
"""

import numpy as np


THRESHOLD = 0.15  # Standard 15% SIC binarization threshold
CELL_AREA_KM2 = 625.0  # EASE-Grid 2.0, 25 km resolution


def binarize(sic: np.ndarray, threshold: float = THRESHOLD) -> np.ndarray:
    """Convert SIC field to binary ice/open-water mask."""
    return (sic >= threshold).astype(np.float32)


def compute_iiee(
    forecast: np.ndarray,
    observed: np.ndarray,
    threshold: float = THRESHOLD,
    cell_area: float = CELL_AREA_KM2,
) -> dict:
    """Compute IIEE decomposition between forecast and observed SIC fields.

    Parameters
    ----------
    forecast : np.ndarray
        Forecast SIC field (values 0-1).
    observed : np.ndarray
        Observed/reference SIC field (values 0-1).
    threshold : float
        Binarization threshold (default 0.15).
    cell_area : float
        Grid cell area in km² (default 625 for EASE-Grid 2.0 at 25 km).

    Returns
    -------
    dict with keys: rmse, mae, iiee, aee, me, me_iiee_ratio, oe_area, ue_area
    """
    valid = np.isfinite(forecast) & np.isfinite(observed)
    f = forecast[valid]
    o = observed[valid]

    # Continuous-field metrics
    rmse = float(np.sqrt(np.mean((f - o) ** 2)))
    mae = float(np.mean(np.abs(f - o)))

    # Binarize
    bf = (f >= threshold).astype(int)
    bo = (o >= threshold).astype(int)

    # Over/under estimation
    oe = np.sum((bf == 1) & (bo == 0)) * cell_area  # Overestimation
    ue = np.sum((bf == 0) & (bo == 1)) * cell_area  # Underestimation

    # IIEE decomposition (Goessling et al. 2016, Eq. 1-3)
    aee = abs(oe - ue)
    me = 2.0 * min(oe, ue)
    iiee = aee + me

    me_iiee_ratio = me / iiee if iiee > 0 else 0.0

    return {
        "rmse": rmse,
        "mae": mae,
        "iiee": iiee,
        "aee": aee,
        "me": me,
        "me_iiee_ratio": me_iiee_ratio,
        "oe_area": oe,
        "ue_area": ue,
    }


def is_fit_for_navigation(
    metrics: dict,
    rmse_threshold: float = 0.10,
    me_iiee_threshold: float = 0.50,
) -> bool:
    """Check if a forecast passes the fitness-for-navigation criterion."""
    return (
        metrics["rmse"] < rmse_threshold
        and metrics["me_iiee_ratio"] < me_iiee_threshold
    )


def is_disagreement(
    metrics: dict,
    rmse_threshold: float = 0.10,
    me_iiee_threshold: float = 0.50,
) -> bool:
    """Check if RMSE approves but IIEE decomposition rejects the forecast."""
    return (
        metrics["rmse"] < rmse_threshold
        and metrics["me_iiee_ratio"] > me_iiee_threshold
    )
