from dataclasses import dataclass
import numpy as np

@dataclass
class SimulationConfig:
    world_adult_population: int = 5_728_759_000
    annual_prevalence_per_100k: int = 53
    prop_chronic: float = 0.20
    prop_episodic: float = 1 - prop_chronic
    prop_treated: float = 0.43
    prop_untreated: float = 1 - prop_treated
    percent_of_patients_to_simulate: float = 0.02
    transformation_method: str = 'linear'
    transformation_display: str = 'Linear'
    max_value: int = 1
    power: float = 2.0
    base: float = np.e
    n_taylor: int = 2
    scaling_factor: float = 1.0
    ms_mean: float = 1.5
    ms_median: float = 3.5
    ms_std: float = 1.8
    ms_prevalence_per_100k: int = 37
    ms_fraction_of_year_in_pain: float = .25
    theme: str = 'dark'