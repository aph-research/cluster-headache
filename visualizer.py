import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import streamlit as st

class Visualizer:
    def __init__(self, simulation):
        self.simulation = simulation
        self.results = simulation.get_results()
        self.intensities = self.results['intensities']
        self.intensities_transformed = self.results['intensities_transformed']
        self.group_data = self.results['group_data']
        self.global_person_years = self.results['global_person_years']
        self.global_std_person_years = self.results['global_std_person_years']
        self.ch_groups = self.results['ch_groups']
        self.ms_data = self.results['ms_data']
        self.color_map = {
            'Episodic Treated': px.colors.qualitative.Plotly[0],
            'Episodic Untreated': px.colors.qualitative.Plotly[1],
            'Chronic Treated': px.colors.qualitative.Plotly[2],
            'Chronic Untreated': px.colors.qualitative.Plotly[3],
            'MS': px.colors.qualitative.Plotly[5]
        }
        self.marker_map = {
            'Episodic Treated': 'cross',
            'Episodic Untreated': 'diamond',
            'Chronic Treated': 'square',
            'Chronic Untreated': 'circle',
            'MS': 'triangle-up'
        }
        self.template = 'plotly_dark' if simulation.config.theme == 'dark' else 'plotly_white'
        self.text_color ='white' if simulation.config.theme == 'dark' else 'black'
        self.zerolinecolor = 'white' if simulation.config.theme == 'dark' else 'black'

    def create_plot(self, data, title, y_title):
        fig = go.Figure()

        for i, (name, values, std) in enumerate(data):
            color = self.color_map[name]
            rgb_color = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
            marker = self.marker_map[name]
            
            # Lower bound of shaded area
            fig.add_trace(go.Scatter(
                x=self.intensities,
                y=[max(0, v - s) for v, s in zip(values, std)],
                mode='lines',
                line=dict(width=0),
                showlegend=False,
                hoverinfo='skip'
            ))
            
            # Upper bound of shaded area
            fig.add_trace(go.Scatter(
                x=self.intensities,
                y=[v + s for v, s in zip(values, std)],
                mode='lines',
                line=dict(width=0),
                fill='tonexty',
                fillcolor=f'rgba({rgb_color[0]},{rgb_color[1]},{rgb_color[2]},0.2)',
                showlegend=False,
                hoverinfo='skip'
            ))
            
            # Main line with markers
            fig.add_trace(go.Scatter(
                x=self.intensities,
                y=values,
                mode='lines+markers',
                name=name,
                line=dict(color=color, width=2),
                marker=dict(
                    symbol=marker,
                    size=[8 if x.is_integer() else 0 for x in self.intensities],
                    color=color,
                ),
                hoverinfo='x+y+name'
            ))

        fig.update_layout(
            title=title,
            xaxis_title='Pain intensity',
            yaxis_title=y_title,
            xaxis=dict(tickmode='linear', tick0=0, dtick=1, tickfont=dict(color=self.text_color), title_font=dict(color=self.text_color)),
            yaxis=dict(tickformat=',.0f', tickfont=dict(color=self.text_color), title_font=dict(color=self.text_color)),
            legend_title_text='',
            hovermode='closest',
            template=self.template,
            legend=dict(
                itemsizing='constant',
                itemwidth=30,
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01,
                bordercolor="grey",
                borderwidth=1
            )
        )

        return fig

    def create_average_hours_plot(self):
        avg_data = [(name, np.array(avg)/60, np.array(std)/60) for name, avg, std, _, _ in self.group_data]
        return self.create_plot(avg_data, 
                                'Average hours per year spent at different pain intensities (±1σ)',
                                'Average hours per year')

    def create_global_person_years_plot(self):
        global_data = [(name, self.global_person_years[name], self.global_std_person_years[name]) 
                       for name in self.ch_groups.keys()]
        return self.create_plot(global_data,
                                'Global annual person-years spent in cluster headaches by intensity (±1σ)',
                                'Global person-years per year')

    def create_bar_plot(self, groups, values, errors, title, y_title):
        fig = go.Figure(data=[
            go.Bar(
                x=groups,
                y=values,
                error_y=dict(type='data', array=errors, visible=True),
                marker=dict(
                    color=[self.color_map[group] for group in groups],
                    opacity=0.7,
                    line=dict(width=1, color='white')
                )
            )
        ])
        
        fig.update_layout(
            title=title,
            yaxis_title=y_title,
            template=self.template,
            xaxis=dict(tickfont=dict(color=self.text_color), title_font=dict(color=self.text_color)),
            yaxis=dict(tickformat=',.0f', tickfont=dict(color=self.text_color), title_font=dict(color=self.text_color)),
            showlegend=False,
            bargap=0.3
        )
        return fig

    def create_total_person_years_plot(self):
        groups = list(self.ch_groups.keys())
        total_values = [sum(self.global_person_years[name]) for name in groups]
        total_error = [np.sqrt(sum(std**2)) for std in self.global_std_person_years.values()]
        
        return self.create_bar_plot(groups,
                                    total_values,
                                    total_error,
                                    'Total estimated person-years spent in cluster headaches annually by group (±1σ)',
                                    'Total person-years')

    def create_high_intensity_person_years_plot(self):
        groups = list(self.ch_groups.keys())
        high_intensity_values = [sum(years[90:]) for years in self.global_person_years.values()]
        high_intensity_error = [np.sqrt(sum(std[90:]**2)) for std in self.global_std_person_years.values()]
        
        return self.create_bar_plot(groups,
                                    high_intensity_values,
                                    high_intensity_error,
                                    'Estimated person-years spent in cluster headaches annually by group (intensity ≥9/10) (±1σ)',
                                    'Person-years (intensity ≥9/10)')

    def create_comparison_plot(self):
        total_all_groups = sum(sum(years) for years in self.global_person_years.values())
        total_all_groups_std = np.sqrt(sum(sum(std**2) for std in self.global_std_person_years.values()))

        intensity_all_groups_7 = sum(sum(years[70:]) for years in self.global_person_years.values())
        intensity_all_groups_7_std = np.sqrt(sum(sum(std[70:]**2) for std in self.global_std_person_years.values()))        

        intensity_all_groups_9 = sum(sum(years[90:]) for years in self.global_person_years.values())
        intensity_all_groups_9_std = np.sqrt(sum(sum(std[90:]**2) for std in self.global_std_person_years.values()))
        
        bar_values = [total_all_groups, intensity_all_groups_7, intensity_all_groups_9]
        bar_errors = [total_all_groups_std, intensity_all_groups_7_std, intensity_all_groups_9_std]
        
        fig = go.Figure(data=[
            go.Bar(
                x=['Total person-years', 'Person-years at ≥7/10 intensity', 'Person-years at ≥9/10 intensity'],
                y=bar_values,
                error_y=dict(type='data', array=bar_errors, visible=True),
                marker=dict(
                    color=['blue', 'red'],
                    opacity=0.7,
                    line=dict(width=1, color='white')
                )
            )
        ])

        fig.update_layout(
            title='Comparison of total, ≥7/10, and ≥9/10 intensity person-years across all groups (±1σ)',
            yaxis_title='Person-Years',
            template=self.template,
            xaxis=dict(tickfont=dict(color=self.text_color), title_font=dict(color=self.text_color)),
            yaxis=dict(tickformat=',.0f', tickfont=dict(color=self.text_color), title_font=dict(color=self.text_color)),
            showlegend=False,
            bargap=0.3
        )

        return fig
    
    def create_adjusted_pain_units_plot(self):
        adjusted_data = []
        for name in self.results['ch_groups'].keys():
            values = self.simulation.adjusted_pain_units[name]
            std = [0] * len(values)
            adjusted_data.append((name, values, std))

        fig_adjusted = go.Figure()
        fig_adjusted = self.create_plot(
            adjusted_data,
            title=f"Annual intensity-adjusted person-years by cluster headache group ({self.simulation.config.transformation_method} transformation)",
            y_title="Annual intensity-adjusted person-years"
        )

        max_adjusted_value = max(max(values) for _, values, _ in adjusted_data)
        fig_adjusted.update_layout(yaxis=dict(range=[0, max_adjusted_value * 1.1]))

        return fig_adjusted

    def create_adjusted_pain_units_plot_comparison_ms(self, pain_threshold=0):
        idx = int(pain_threshold * 10)

        if pain_threshold > 0:
            title = f"Annual intensity-adjusted person-years of ≥{int(pain_threshold)}/10 pain: Multiple sclerosis vs cluster headache <br>({self.simulation.config.transformation_method} transformation)"
            size = [8 for _ in self.intensities]
            xaxis_ticks=dict(tickmode='array', dtick=0.1, range=[pain_threshold-0.1, 10.1], tickfont=dict(color=self.text_color), title_font=dict(color=self.text_color))
        else:
            title = f"Annual intensity-adjusted person-years of pain: Multiple sclerosis vs cluster headache <br>({self.simulation.config.transformation_method} transformation)"
            size = [8 if x.is_integer() else 0 for x in self.intensities]
            xaxis_ticks=dict(tickmode='linear', tick0=0, dtick=1, tickfont=dict(color=self.text_color), title_font=dict(color=self.text_color))

        global_person_years_ch_all_adjusted = sum(self.simulation.adjusted_pain_units[group] for group in self.simulation.adjusted_pain_units.keys())
        
        fig = go.Figure()
        
        # Plot the global_person_years_ch_all as another line with markers
        fig.add_trace(go.Scatter(
            x=self.intensities[idx:],
            y=global_person_years_ch_all_adjusted[idx:],
            mode='lines+markers',
            name='Cluster Headache',
            line=dict(color=self.color_map['Episodic Untreated'], width=2),
            marker=dict(
                    symbol=self.marker_map['Episodic Untreated'],
                    size=size,
                    color=self.color_map['Episodic Untreated'],
                ),
            hoverinfo='x+y+name'
        ))
        
        fig.add_trace(go.Scatter(
            x=self.intensities[idx:],
            y=self.simulation.adjusted_pain_units_ms[idx:],
            mode='lines+markers',
            name='Multiple Sclerosis',
            line=dict(color=self.color_map['MS'], width=2),
            marker=dict(
                    symbol=self.marker_map['MS'],
                    size=size,
                    color=self.color_map['MS'],
                ),
            hoverinfo='x+y+name'
        ))

        fig.update_layout(
            title=title,
            xaxis_title='Pain intensity',
            xaxis=xaxis_ticks,
            legend_title_text='',
            yaxis=dict(
                title='Intensity-adjusted person-years',
                tickformat=',.0f',
                tickfont=dict(color=self.text_color), 
                title_font=dict(color=self.text_color)
            ),

            legend=dict(
                itemsizing='constant',
                itemwidth=30,
                yanchor="top",
                y=0.95,
                xanchor="left",
                x=0.01,
                #bgcolor="rgba(0,0,0,0.5)",
                bordercolor="grey",
                borderwidth=1
            ),
            template=self.template
        )

        return fig
    
    def create_adjusted_pain_units_plot_comparison_ms_3d(self, pain_threshold=0):
        idx = int(pain_threshold * 10)

        if pain_threshold > 0:
            title_3d = f"Annual intensity-adjusted person-years of ≥{int(pain_threshold)}/10 pain: Multiple sclerosis vs cluster jeadache"
            title_transformation = f"Intensity transformation for which ≥{int(pain_threshold)}/10 CH burden > MS burden"
        else:
            title_3d = f"Annual intensity-adjusted person-years of pain: Multiple sclerosis vs cluster headache"
            title_transformation = f"Intensity transformation for which total CH burden > MS burden"
        
        fig = go.Figure()
        fig_intensities = go.Figure()

        # Define the range for n_taylor
        n_taylor_values = range(2, 36)
        n_taylor_crossing = 0

        # Prepare data for 3D plot
        intensities = self.intensities[idx:]
        intensities_transformed = self.intensities_transformed[idx:]
        z_data_ms = []
        z_data_cluster = []

        # Store the current configuration
        original_transformation_method = self.simulation.config.transformation_method
        original_transformation_display = self.simulation.config.transformation_display
        original_n_taylor = self.simulation.config.n_taylor

        for n_taylor in n_taylor_values:
            # Temporarily change the configuration
            self.simulation.config.transformation_method = 'taylor'
            self.simulation.config.transformation_display = 'Taylor'
            self.simulation.config.n_taylor = n_taylor

            # Recalculate adjusted pain units
            self.simulation.calculate_adjusted_pain_units()
            
            adjusted_pain_units_ms = self.simulation.adjusted_pain_units_ms[idx:]
            z_data_ms.append(adjusted_pain_units_ms)
            total_ms_burden = sum(adjusted_pain_units_ms)
            
            # Calculate the global adjusted pain units for cluster headaches
            global_person_years_ch_all_adjusted = np.zeros_like(adjusted_pain_units_ms)
            for group in self.simulation.ch_groups.keys():
                global_person_years_ch_all_adjusted += self.simulation.adjusted_pain_units[group][idx:]
            
            z_data_cluster.append(global_person_years_ch_all_adjusted)
            total_cluster_burden = sum(global_person_years_ch_all_adjusted)

            if total_cluster_burden > total_ms_burden and n_taylor_crossing == 0:
                n_taylor_crossing = n_taylor
                intensities_transformed = self.simulation.intensities_transformed[idx:]

        # Reset the original configuration
        self.simulation.config.transformation_method = original_transformation_method
        self.simulation.config.transformation_display = original_transformation_display
        self.simulation.config.n_taylor = original_n_taylor

        # Recalculate with original configuration
        self.simulation.calculate_adjusted_pain_units()

        # Convert z_data to a 2D arrays
        z_data_ms = np.array(z_data_ms)
        z_data_cluster = np.array(z_data_cluster)
    
        # Create the 3D surface plot for ms
        fig.add_trace(go.Surface(
            x=intensities,
            y=np.array(n_taylor_values)-2,
            z=z_data_ms,
            colorscale='Blues_r',
            name='MS',
            opacity=0.99,
            showscale=False,
            hovertemplate='Intensity: %{x}<br>Adj. person-years: %{z:,.0f}'
        ))
        
        # Create the 3D surface plot for cluster headache
        fig.add_trace(go.Surface(
            x=intensities,
            y=np.array(n_taylor_values)-2,
            z=z_data_cluster,
            colorscale='Sunsetdark',
            name='CH',
            opacity=0.7,
            showscale=False,
            hovertemplate='Intensity: %{x}<br>Adj. person-years: %{z:,.0f}'
        ))

        # Add the plane at n_taylor_crossing-2 if it is not zero
        # (subtracting 2 since n_taylor starts at 2, which corresponds to y = 0)
        if n_taylor_crossing != 0:
            plane_y = np.full((len(intensities), len(z_data_cluster[0])), n_taylor_crossing-2)
            max_z_value = np.max([np.max(z_data_cluster), np.max(z_data_ms)])
            plane_z = np.linspace(0, max_z_value, len(z_data_cluster[0]))
            plane_z = np.tile(plane_z, (len(intensities), 1))

            fig.add_trace(go.Surface(
                x=np.tile(intensities, (len(z_data_cluster[0]), 1)).T,
                y=plane_y,
                z=plane_z,
                colorscale=[[0, 'rgba(255, 0, 0, 0.5)'], [1, 'rgba(255, 0, 0, 0.5)']],
                name='Crossing Plane',
                showscale=False,
                hovertemplate='Point where CH burden > MS burden<extra></extra>'
            ))
            
            fig_intensities.add_trace(go.Scatter(
                x=intensities,
                y=intensities_transformed,
                mode='lines+markers',
                marker=dict(
                    size=[8 if x.is_integer() else 0 for x in intensities],
                ),
                name='Adjusted intensities'
            ))

            # Update layout
            fig_intensities.update_layout(
                title=title_transformation,
                xaxis_title='Pain intensity',
                yaxis_title='Weight',
                template=self.template,
                xaxis=dict(
                    tickmode='array',
                    tickvals=[int(i) for i in intensities],
                    ticktext=[str(int(i)) for i in intensities],
                    tickfont=dict(color=self.text_color), 
                    title_font=dict(color=self.text_color),
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='lightgray',
                    zeroline=True,
                    zerolinewidth=2,
                    zerolinecolor=self.zerolinecolor
                    ),
                yaxis=dict(
                    tickmode='array',
                    tickvals=[i/10 for i in range(11)],
                    ticktext=[f'{i/10:.1f}' for i in range(11)],
                    tickfont=dict(color=self.text_color), 
                    title_font=dict(color=self.text_color),
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='lightgray',
                    zeroline=True,
                    zerolinewidth=2,
                    zerolinecolor=self.zerolinecolor
                    ),
                # Make the plot square
                height=550,
                width=550,
            )

        fig.update_layout(
            title=title_3d,
            scene=dict(
                xaxis=dict(
                    title='Pain intensity',
                    autorange='reversed',
                    tickfont=dict(color=self.text_color),
                    title_font=dict(color=self.text_color)
                ),
                yaxis=dict(
                    title='',
                    tickvals=[n_taylor_values[0]-2, n_taylor_values[-1]-2],
                    ticktext=['More linear', 'More exponential'],
                    tickfont=dict(color=self.text_color), 
                    title_font=dict(color=self.text_color)
                ),
                zaxis=dict(
                    title='Adjusted person-years',
                    tickformat=',.0f',
                    tickfont=dict(color=self.text_color), 
                    title_font=dict(color=self.text_color),
                ),
                aspectratio=dict(x=2, y=2, z=1)
            ),
            scene_camera={
                "eye": {"x": -1.5, "y": 2.25, "z": 0.5},
                "center": {"x": 0.25, "y": 0.0, "z": -0.5},
                "up": {"x": 0.0, "y": 0.0, "z": 1.0}
            },
            template=self.template,
            height=500,
            margin=dict(l=0, r=0, t=50, b=30)
        )

        return fig, fig_intensities
                
    def create_summary_table(self):
        def format_with_adjusted(value, adjusted):
            return f"{value:,.0f} ({adjusted:,.0f})"
    
        table_data = []
        total_row = {
            'Group': 'Total',
            'Average patient': {key: 0 for key in ['Hours', 'High-intensity hours', 'Adjusted units', 'High-intensity adjusted units']},
            'Global estimate': {key: 0 for key in ['Person-years', 'High-intensity person-years', 'Adjusted units', 'High-intensity adjusted units']}
        }

        for group in self.results['ch_groups'].keys():
            avg_data = next(avg for name, avg, _, _, _ in self.results['group_data'] if name == group)
            avg_hours = sum(avg_data)/60
            avg_high_hours = sum(avg_data[90:])/60
            global_years = sum(self.results['global_person_years'][group])
            global_high_years = sum(self.results['global_person_years'][group][90:])

            self.simulation.global_person_years[group] = self.results['global_person_years'][group]
            self.simulation.intensities = self.results['intensities']
            global_adjusted_units = sum(self.simulation.adjusted_pain_units[group])
            avg_adjusted_units = sum(self.simulation.adjusted_avg_pain_units[group])/60
            avg_high_adjusted_units = sum(self.simulation.adjusted_avg_pain_units[group][90:])/60
            global_high_adjusted_units = sum(self.simulation.adjusted_pain_units[group][90:])
            
            row = {
                'Group': group,
                'Average patient': {
                    'Hours': avg_hours,
                    'High-intensity hours': avg_high_hours,
                    'Adjusted units': avg_adjusted_units,
                    'High-intensity adjusted units': avg_high_adjusted_units
                },
                'Global estimate': {
                    'Person-years': global_years,
                    'High-intensity person-years': global_high_years,
                    'Adjusted units': global_adjusted_units,
                    'High-intensity adjusted units': global_high_adjusted_units
                }
            }
            table_data.append(row)
            
            # Update total row
            for category in ['Average patient', 'Global estimate']:
                for key in total_row[category].keys():
                    total_row[category][key] += row[category][key]
        
        table_data.append(total_row)
    
        df_data = [
            {
                'Group': row['Group'],
                'Hours': format_with_adjusted(row['Average patient']['Hours'], row['Average patient']['Adjusted units']),
                'High-intensity hours': format_with_adjusted(row['Average patient']['High-intensity hours'], row['Average patient']['High-intensity adjusted units']),
                'Person-years': format_with_adjusted(row['Global estimate']['Person-years'], row['Global estimate']['Adjusted units']),
                'High-intensity person-years': format_with_adjusted(row['Global estimate']['High-intensity person-years'], row['Global estimate']['High-intensity adjusted units'])
            }
            for row in table_data
        ]
        df = pd.DataFrame(df_data)
        
        df.columns = pd.MultiIndex.from_tuples([
            ('', 'Group'),
            ('Average patient', 'Total hours in pain'),
            ('Average patient', 'Hours in ≥9/10 pain'),
            ('Global estimate', 'Total person-years in pain'),
            ('Global estimate', 'Person-years in ≥9/10 pain')
        ])
        
        return df

    def display_summary_table(self, df):
        css = f"""
        <style>
            .dataframe {{
                width: 100%;
                text-align: right;
                border-collapse: collapse;
                font-size: 0.9em;
                color: #333;
                background-color: #f8f8f8;
                border-left: none;
                border-right: none;
            }}
            .dataframe th, .dataframe td {{
                border-top: 1px solid #ddd;
                border-bottom: 1px solid #ddd;
                border-left: none;
                border-right: none;
                padding: 8px;
                white-space: pre-wrap;
                word-wrap: break-word;
                max-width: 150px;
                text-align: center;
            }}
            .table-title {{
                font-size: 1.0em;
                font-weight: bold;
                text-align: left;
                margin-bottom: 0.5em;
            }}
            .table-subtitle {{
                font-size: 0.8em;
                text-align: left;
                margin-bottom: 1em;
            }}
            .dataframe thead tr:nth-child(1) th {{
                background-color: #e0e0e0;
                text-align: center;
                font-weight: bold;
                color: #333;
            }}
            .dataframe thead tr:nth-child(2) th {{
                background-color: #e8e8e8;
                text-align: center;
                color: #333;
            }}
            .dataframe tbody tr:nth-child(even) {{
                background-color: #f0f0f0;
            }}
            .dataframe tbody tr:nth-child(odd) {{
                background-color: #f8f8f8;
            }}
            .dataframe tbody tr:hover {{
                background-color: #e8e8e8;
            }}
            .dataframe td:first-child, .dataframe th:first-child {{
                text-align: left;
            }}
            .table-note {{
                margin-top: 10px;
                font-style: italic;
                font-size: 0.9em;
            }}
            .dataframe tr:last-child {{
                font-weight: bold;
            }}
            @media (prefers-color-scheme: {self.simulation.config.theme}) {{
                .dataframe, .table-note {{
                    color: #e0e0e0;
                    background-color: #2c2c2c;
                }}
                .dataframe th, .dataframe td {{
                    border-color: #4a4a4a;
                }}
                .dataframe thead tr:nth-child(1) th,
                .dataframe thead tr:nth-child(2) th {{
                    background-color: #3c3c3c;
                    color: #e0e0e0;
                }}
                .dataframe tbody tr:nth-child(even) {{
                    background-color: #323232;
                }}
                .dataframe tbody tr:nth-child(odd) {{
                    background-color: #2c2c2c;
                }}
                .dataframe tbody tr:hover {{
                    background-color: #3a3a3a;
                }}
            }}
        </style>
        """
        table_html = f"""
        <div class="table-title">Intensity-adjusted person-years experienced annually ({self.simulation.config.transformation_method} transformation)</div>
        <div class="table-subtitle">Values in brackets represent intensity-adjusted person-years.</div>
        {df.to_html(classes='dataframe', index=False)}
        """
        st.markdown(css, unsafe_allow_html=True)
        st.write(table_html, unsafe_allow_html=True)
    
    def update_results(self, new_results):
        self.results = new_results

    def create_3d_patient_scatter(self):
        # Note that here we plot the total attack durations, not the time spent at the max intensity level (70% of total duration)
        # Prepare data
        data = []
        
        for group in ['Chronic Untreated', 'Chronic Treated', 'Episodic Untreated', 'Episodic Treated']:
            x = self.results['global_total_attacks'][group]
            y = self.results['global_total_attack_durations'][group]
            y = np.array(y)/60
            z = self.results['global_average_intensity'][group]
            data.append(go.Scatter3d(
                x=x,
                y=y,
                z=z,
                mode='markers',
                name=group,
                marker=dict(
                    size=5,
                    opacity=0.8,
                    symbol=self.marker_map[group],
                    color=self.color_map[group]
                ),
                hovertemplate=
                '<b>%{text}</b><br><br>' +
                'Total attacks: %{x}<br>' +
                'Total duration: %{y:.0f} hours<br>' +
                'Average intensity: %{z:.1f}<extra></extra>',
                text=[group] * len(x)
            ))

        # Create the 3D scatter plot
        fig = go.Figure(data=data)

        # Get camera settings from session state or use default
        factor = 1.0
        camera = st.session_state.get('camera', {
            'eye': {'x': 1.4*factor, 'y': -1.4*factor, 'z': .4*factor},
            'up': {'x': 0, 'y': 0, 'z': 1},
            'center': {'x': 0, 'y': 0, 'z': -.2}
        })

        # Update the layout
        fig.update_layout(
            title='Annual cluster headache attack data by patient group',
            scene=dict(
                xaxis_title='Total attacks',
                yaxis_title='Total duration (hours)',
                zaxis_title='Average intensity',
                aspectmode='manual',
                aspectratio=dict(x=1, y=1, z=0.8),
                camera=camera,
                xaxis=dict(tickfont=dict(color=self.text_color), title_font=dict(color=self.text_color)),
                yaxis=dict(tickfont=dict(color=self.text_color), title_font=dict(color=self.text_color)),
                zaxis=dict(tickfont=dict(color=self.text_color), title_font=dict(color=self.text_color)),
            ),
            margin=dict(t=40, b=0, l=0, r=0),
            autosize=True,
            legend=dict(
                bordercolor='grey',  # White border color
                borderwidth=1,  # Border width
                itemsizing='constant',
                itemwidth=30  # Adjust this value to change the size of legend markers
            ),
            template=self.template,
        )
        return fig
    
    def plot_ch_vs_ms_person_years(self):
        fig = go.Figure()

        global_person_years_ch_all = sum(self.global_person_years[group] for group in self.global_person_years.keys())

        fig.add_trace(go.Scatter(
            x=self.intensities,
            y=global_person_years_ch_all,
            mode='lines+markers',
            name='Cluster Headache',
            line=dict(color=self.color_map['Episodic Untreated'], width=2),
            marker=dict(
                symbol=self.marker_map['Episodic Untreated'],
                size=[8 if x.is_integer() else 0 for x in self.simulation.ms_data['x']],
                color=self.color_map['Episodic Untreated'],
            ),
            hoverinfo='x+y+name'
        ))

        fig.add_trace(go.Scatter(
            x=self.intensities,
            y=self.simulation.ms_data['y'],
            mode='lines+markers',
            name='Multiple Sclerosis',
            line=dict(color=self.color_map['MS'], width=2),
            marker=dict(
                symbol=self.marker_map['MS'],
                size=[8 if x.is_integer() else 0 for x in self.simulation.ms_data['x']],
                color=self.color_map['MS'],
            ),
            hoverinfo='x+y+name'
        ))
        
        fig.update_layout(
            title="Global annual person-years of pain: Multiple sclerosis vs cluster headache",
            xaxis_title='Pain Intensity',
            xaxis=dict(tickmode='linear', tick0=0, dtick=1, tickfont=dict(color=self.text_color), title_font=dict(color=self.text_color)),
            yaxis=dict(
                title='Annual person-years',
                tickfont=dict(color=self.text_color),
                title_font=dict(color=self.text_color),
                tickformat=',.0f'
            ),
            template=self.template,
            legend=dict(
                itemsizing='constant',
                itemwidth=30,
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01,
                bordercolor="grey",
                borderwidth=1
            )
        )

        return fig

    def create_burden_ratio_heatmap(self):
        n_taylor_values = range(2, 25)
        pain_thresholds = np.arange(0, 10.1, 0.5)
        
        original_transformation_method = self.simulation.config.transformation_method
        original_transformation_display = self.simulation.config.transformation_display
        original_n_taylor = self.simulation.config.n_taylor
        
        ratio_matrix = np.zeros((len(pain_thresholds), len(n_taylor_values)))
        original_ratios = np.zeros_like(ratio_matrix)
        
        for i, threshold in enumerate(pain_thresholds):
            idx = int(threshold * 10)
            
            for j, n_taylor in enumerate(n_taylor_values):
                self.simulation.config.transformation_method = 'taylor'
                self.simulation.config.transformation_display = 'Taylor'
                self.simulation.config.n_taylor = n_taylor
                
                self.simulation.calculate_adjusted_pain_units()
                
                ch_burden = sum(sum(group[idx:]) for group in self.simulation.adjusted_pain_units.values())
                ms_burden = sum(self.simulation.adjusted_pain_units_ms[idx:])
                
                if ms_burden > 0:
                    ratio = ch_burden / ms_burden
                    original_ratios[i, j] = ratio
                    ratio_matrix[i, j] = np.log10(ratio) if ratio > 0 else np.nan
                else:
                    ratio_matrix[i, j] = np.nan
                    original_ratios[i, j] = np.nan
        
        max_abs_val = max(abs(np.nanmin(ratio_matrix)), abs(np.nanmax(ratio_matrix)))
        
        fig = go.Figure(data=go.Heatmap(
            x=list(n_taylor_values),
            y=pain_thresholds,
            z=ratio_matrix,
            colorscale='RdBu',
            zmid=0,
            zmin=-max_abs_val,
            zmax=max_abs_val,
            colorbar=dict(
                title=dict(
                    text='log₁₀(CH:MS Burden Ratio)',
                    font=dict(color=self.text_color)
                ),
                ticktext=[f'1/{10**i}' for i in range(int(max_abs_val), 0, -1)] +
                        ['1'] +
                        [f'{10**i}' for i in range(1, int(max_abs_val)+1)],
                tickvals=[-i for i in range(int(max_abs_val), 0, -1)] +
                        [0] +
                        [i for i in range(1, int(max_abs_val)+1)],
                tickfont=dict(color=self.text_color)  # Added this line
            ),
            hovertemplate='Taylor Terms: %{x}<br>' +
                        'Pain Threshold: %{y:.1f}<br>' +
                        'CH:MS Ratio: %{customdata:.3f}<extra></extra>',
            customdata=original_ratios
        ))
        
        fig.add_trace(go.Contour(
            x=list(n_taylor_values),
            y=pain_thresholds,
            z=ratio_matrix,
            contours=dict(
                coloring='none',
                showlabels=False,  # Changed to False
                start=0,
                end=0,
                size=0
            ),
            line=dict(color='black', width=2),
            showscale=False,
            hoverinfo='skip'
        ))
        
        fig.update_layout(
            title='CH:MS burden ratio by transformation intensity transformation and pain threshold',
            xaxis=dict(
                title='Intensity scale transformation',
                ticktext=['More linear', 'More exponential'],
                tickvals=[n_taylor_values[0], n_taylor_values[-1]],
                tickfont=dict(color=self.text_color), 
                title_font=dict(color=self.text_color)
            ),
            yaxis=dict(
                title='Minimum pain intensity threshold',
                tickformat='.1f',
                tickfont=dict(color=self.text_color), 
                title_font=dict(color=self.text_color)
            ),
            width=800,
            height=600,
            template=self.template
        )
        
        self.simulation.config.transformation_method = original_transformation_method
        self.simulation.config.transformation_display = original_transformation_display
        self.simulation.config.n_taylor = original_n_taylor
        self.simulation.calculate_adjusted_pain_units()
        
        return fig