import numpy as np
from collections import defaultdict
from models import Patient
from stats_utils import calculate_adjusted_pain_units, calculate_ms_distribution

class Simulation:
    def __init__(self, config):
        self.config = config
        self.population = []
        self.results = None
        self.intensities = np.arange(0, 10.1, 0.1)
        self.intensities_transformed = np.array([])
        self.ch_groups = None
        self.global_person_years = {}
        self.global_std_person_years = {}
        self.global_total_attacks = {}
        self.global_total_attack_durations = {}
        self.global_average_intensity = {}
        self.adjusted_pain_units = {}
        self.adjusted_avg_pain_units = {}
        self.adjusted_pain_units_ms = np.array([])
        self.group_data = []
        self.total_ch_sufferers = None
        self.ms_data = []

    def run(self):
        self.calculate_ch_groups()
        self.generate_population()
        self.simulate_year()
        self.calculate_results()

    def calculate_ch_groups(self):
        self.total_ch_sufferers = self.config.world_adult_population * self.config.annual_prevalence_per_100k / 100_000

        self.ch_groups = {
            'Episodic Treated': int(self.total_ch_sufferers * self.config.prop_episodic * self.config.prop_treated),
            'Episodic Untreated': int(self.total_ch_sufferers * self.config.prop_episodic * self.config.prop_untreated),
            'Chronic Treated': int(self.total_ch_sufferers * self.config.prop_chronic * self.config.prop_treated),
            'Chronic Untreated': int(self.total_ch_sufferers * self.config.prop_chronic * self.config.prop_untreated)
        }

    def get_total_ch_sufferers(self):
        return int(self.total_ch_sufferers)
    
    def get_simulated_patients_info(self):
        fraction = self.config.percent_of_patients_to_simulate / 100
        total_simulated = int(sum(self.ch_groups.values()) * fraction)
        group_info = []
        for group, count in self.ch_groups.items():
            simulated_count = int(count * fraction)
            percentage = round(simulated_count / total_simulated * 100)
            group_info.append((group, simulated_count, percentage))
        return total_simulated, group_info
    
    def generate_population(self):
        fraction = self.config.percent_of_patients_to_simulate / 100
        for group, total in self.ch_groups.items():
            n_patients = int(total * fraction)
            is_chronic = 'Chronic' in group
            is_treated = 'Treated' in group
            for _ in range(n_patients):
                self.population.append(Patient(is_chronic, is_treated))

    def simulate_year(self):
        for patient in self.population:
            patient.generate_year_of_attacks()

    def calculate_results(self):
        group_data = []
        global_person_years = {}
        global_std_person_years = {}
        global_total_attacks = defaultdict(list)
        global_total_attack_durations = defaultdict(list)
        global_average_intensity = defaultdict(list)

        for group_name, condition in [
            ("Episodic Treated", lambda p: not p.is_chronic and p.is_treated),
            ("Episodic Untreated", lambda p: not p.is_chronic and not p.is_treated),
            ("Chronic Treated", lambda p: p.is_chronic and p.is_treated),
            ("Chronic Untreated", lambda p: p.is_chronic and not p.is_treated)
        ]:
            group_patients = [p for p in self.population if condition(p)]
            total_intensity_minutes = {}
            intensity_minutes_list = {round(i, 1): [] for i in self.intensities}
            
            for patient in group_patients:
                patient_intensity_minutes = patient.calculate_intensity_minutes()
                for intensity, minutes in patient_intensity_minutes.items():
                    rounded_intensity = round(intensity, 1)
                    total_intensity_minutes[rounded_intensity] = total_intensity_minutes.get(rounded_intensity, 0) + minutes
                    intensity_minutes_list[rounded_intensity].append(minutes)
                global_total_attacks[group_name].append(patient.calculate_total_attacks())
                global_total_attack_durations[group_name].append(patient.calculate_total_duration())
                global_average_intensity[group_name].append(patient.calculate_average_intensity())

            n_patients = len(group_patients)
            if n_patients > 0:
                intensity_minutes_average = [total_intensity_minutes.get(round(i, 1), 0) / n_patients for i in self.intensities]
                intensity_minutes_std = [np.std(intensity_minutes_list[round(i, 1)]) if intensity_minutes_list[round(i, 1)] else 0 for i in self.intensities]
                intensity_minutes_total = [total_intensity_minutes.get(round(i, 1), 0) for i in self.intensities]
            else:
                intensity_minutes_average = [0 for _ in self.intensities]
                intensity_minutes_std = [0 for _ in self.intensities]
                intensity_minutes_total = [0 for _ in self.intensities]
            
            group_data.append((group_name, intensity_minutes_average, intensity_minutes_std, intensity_minutes_total, n_patients))

            global_total = self.ch_groups[group_name]
            global_person_years[group_name] = np.array([(a * global_total) / (60 * 24 * 365) for a in intensity_minutes_average])
            global_std_person_years[group_name] = np.array([(s * global_total) / (60 * 24 * 365) for s in intensity_minutes_std])

        self.group_data = group_data
        self.global_person_years = global_person_years
        self.global_std_person_years = global_std_person_years
        self.global_total_attacks = global_total_attacks
        self.global_total_attack_durations = global_total_attack_durations
        self.global_average_intensity = global_average_intensity

    def calculate_adjusted_pain_units(self):
        for group in self.ch_groups.keys():
            self.adjusted_pain_units[group], self.intensities_transformed = calculate_adjusted_pain_units(
                self.global_person_years[group],
                self.intensities,
                self.config.transformation_method,
                self.config.power,
                self.config.max_value,
                self.config.base,
                self.config.scaling_factor,
                self.config.n_taylor
            )
            avg_data = next(avg for name, avg, _, _, _ in self.group_data if name == group)
            self.adjusted_avg_pain_units[group], _ = calculate_adjusted_pain_units(
                avg_data,
                self.intensities,
                self.config.transformation_method,
                self.config.power,
                self.config.max_value,
                self.config.base,
                self.config.scaling_factor,
                self.config.n_taylor
            )
        self.adjusted_pain_units_ms, self.intensities_transformed = calculate_adjusted_pain_units(
            self.ms_data['y'],
            self.intensities,
            self.config.transformation_method,
            self.config.power,
            self.config.max_value,
            self.config.base,
            self.config.scaling_factor,
            self.config.n_taylor
        )

    def calculate_ms_data(self):
        self.ms_data = defaultdict(list)
        self.ms_data['x'], self.ms_data['y'] = calculate_ms_distribution(
            self.config.ms_mean,
            self.config.ms_median,
            self.config.ms_std
        )
        total_ms_sufferers = self.config.world_adult_population * (self.config.ms_prevalence_per_100k / 100_000)
        # Need to multiply by 0.1 since otherwise I get the distribution only, but the time is the integral, with bin width 0.1
        # Also need to multiply by the hours spent awake (16/24), since 100% of time in pain should be of time awake
        self.ms_data['y'] = self.ms_data['y'] * total_ms_sufferers * self.config.ms_fraction_of_year_in_pain * (16/24) * 0.1

    def update_transformation_params(self, transformation_method, transformation_display, power, base, scaling_factor, ms_mean, ms_median, ms_std, ms_prevalence_per_100k, ms_fraction_of_year_in_pain):
        self.config.transformation_method = transformation_method
        self.config.transformation_display = transformation_display
        self.config.power = power
        self.config.base = base
        self.config.scaling_factor = scaling_factor
        self.config.ms_mean = ms_mean
        self.config.ms_median = ms_median
        self.config.ms_std = ms_std
        self.config.ms_prevalence_per_100k = ms_prevalence_per_100k
        self.config.ms_fraction_of_year_in_pain = ms_fraction_of_year_in_pain
        self.calculate_ms_data()
        self.calculate_adjusted_pain_units()

    def get_results(self):
        return {
            'config': self.config,
            'intensities': self.intensities,
            'intensities_transformed': self.intensities_transformed,
            'group_data': self.group_data,
            'global_person_years': self.global_person_years,
            'global_std_person_years': self.global_std_person_years,
            'global_total_attacks': self.global_total_attacks,
            'global_total_attack_durations': self.global_total_attack_durations,
            'global_average_intensity': self.global_average_intensity,
            'ch_groups': self.ch_groups,
            'adjusted_pain_units': self.adjusted_pain_units,
            'adjusted_avg_pain_units': self.adjusted_avg_pain_units,
            'ms_data': self.ms_data
        }