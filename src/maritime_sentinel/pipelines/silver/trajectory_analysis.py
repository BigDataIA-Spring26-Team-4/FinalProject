"""MovingPandas trajectory analysis on AIS positions.

Computes: stop detection, transit times, speed anomalies.
"""


def compute_trajectories(chokepoint_id: str) -> dict:
    """Run MovingPandas trajectory analysis on Silver vessel positions."""
    # TODO: Create TrajectoryCollection from silver_vessel_positions
    # TODO: detect_stops(duration=timedelta(hours=2))
    # TODO: compute transit times between entry/exit of chokepoint bbox
    raise NotImplementedError
