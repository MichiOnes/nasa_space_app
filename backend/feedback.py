import json
import matplotlib.pyplot as plt
import numpy as np
import io
import base64
from IPython.display import display, Image
import datetime
from user import get_climate_at_location



def data_at_location(data, category, lat_target, lon_target, monthly_mean=False, plot=False,
                     bin_years=5, start_year=1940, year_range=None):
    """
    Extract a variable at a given lat/lon from the combined dataset.

    Parameters:
        data : dict
            Dictionary containing variables with dimensions (time, lat, lon) and 'lat', 'lon', 'time'
        category : str
            Name of the variable to extract (must be a key in data)
        lat_target : float
            Latitude of the point of interest
        lon_target : float
            Longitude of the point of interest
        monthly_mean : bool
            If True, return mean per calendar month (Jan-Dec)
            If False, return evolution over time binned by bin_years
        plot : bool
            If True, generate a plot
        bin_years : int
            Number of years per bin when monthly_mean=False
        start_year : int
            Year corresponding to the first time step in the dataset
        year_range : tuple of (int, int) or None
            If monthly_mean=True, restrict analysis to years in [from_year, to_year]
            Example: year_range=(1980,2020)

    Returns:
        values : np.array
            Extracted values (monthly mean: 12 values, otherwise binned)
        time_index : np.array of months or bin start years
    """

    # Load lat/lon/time
    lat = data['lat']
    lon = data['lon']
    time_len = len(data['time'])
    data_var = data[category]  # shape (time, lat, lon)

    # Find nearest grid point
    lat_idx = np.abs(lat - lat_target).argmin()
    lon_idx = np.abs(lon - lon_target).argmin()

    # Extract time series at grid point
    ts = data_var[:, lat_idx, lon_idx]

    # Create datetime array assuming monthly time steps
    time_index = np.array([datetime.datetime(start_year + i//12, (i%12)+1, 1) for i in range(time_len)])
    years = np.array([t.year for t in time_index])

    if monthly_mean:
        # Filter by year_range if provided
        if year_range is not None:
            from_year, to_year = year_range
            if not (isinstance(from_year, int) and isinstance(to_year, int)):
                raise ValueError("year_range must be a tuple of two integers (from_year, to_year)")
            if to_year <= from_year:
                raise ValueError("to_year must be greater than from_year")
            if from_year < start_year:
                raise ValueError(f"from_year must be >= {start_year}")
            mask = (years >= from_year) & (years <= to_year)
            ts = ts[mask]
            time_index_filtered = time_index[mask]
        else:
            time_index_filtered = time_index

        # Compute monthly mean
        months = np.array([t.month for t in time_index_filtered])
        monthly_avg = np.array([ts[months == m].mean() for m in range(1, 13)])

        if plot:
            plt.figure(figsize=(8,4))
            plt.bar(range(1,13), monthly_avg)
            plt.xticks(range(1,13))
            plt.xlabel('Month')
            plt.ylabel(category)
            title_years = f"from {from_year} to {to_year}" if year_range else ""
            plt.title(f'Average {category} per Month at lat={lat_target}, lon={lon_target} {title_years}')
            plt.show()

        return monthly_avg, np.arange(1,13)

    else:
        # Bin time series into bin_years periods
        start_bin = years.min()
        end_bin = years.max()
        bins = np.arange(start_bin, end_bin + bin_years, bin_years)

        binned_values = []
        bin_centers = []

        for i in range(len(bins)-1):
            mask = (years >= bins[i]) & (years < bins[i+1])
            if np.any(mask):
                binned_values.append(ts[mask].mean())
                bin_centers.append(bins[i])

        binned_values = np.array(binned_values)
        bin_centers = np.array(bin_centers)

        if plot:
            plt.figure(figsize=(10,4))
            plt.plot(bin_centers, binned_values, marker='o', linestyle='-')
            plt.xlabel('Year')
            plt.ylabel(category)
            plt.title(f'{category} Evolution at lat={lat_target}, lon={lon_target} ({bin_years}-year bins)')
            plt.show()

        return binned_values, bin_centers


def provide_feedback_plot(lat, lon, data, fb_vars):
    """
    Plot climate variables and return as base64 string.
    """
    months = np.arange(1, 13)
    fig, ax1 = plt.subplots(figsize=(12, 4))
    
    primary_vars = ['precipitation', 'evaporation', 'soil_moisture']
    secondary_vars = ['temperature', 'frost_days']
    
    ax2_created = False
    for var in fb_vars:
        var = var.strip()  # remove extra spaces
        values, _ = data_at_location(data, var, lat, lon, monthly_mean=True, year_range=(2014,2024))
        if var in primary_vars:
            ax1.plot(months, values, '-o', label=var.replace('_',' ').title())
        elif var in secondary_vars:
            if not ax2_created:
                ax2 = ax1.twinx()
                ax2_created = True
            ax2.plot(months, values, '-s', label=var.replace('_',' ').title())
    
    ax1.set_xlabel('Month')
    ax1.set_xticks(months)
    ax1.set_ylabel('Primary variables')
    if ax2_created:
        ax2.set_ylabel('Secondary variables')
    
    # Combine legends
    lines, labels = ax1.get_legend_handles_labels()
    if ax2_created:
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines + lines2, labels + labels2, loc='upper right')
    else:
        ax1.legend(lines, labels, loc='upper right')
    
    plt.title(f'Climate Data at lat={lat}, lon={lon} (2014-2024)')
    
    # Save plot to base64
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    return img_base64

def generate_feedback(user_json, data):
    """
    Generate textual feedback and plot for user's answer.
    
    user_json should contain:
    {
      "category": "...",
      "qid": "...",
      "text": "...",
      "options": {...},
      "selected_answer": "C",
      "correct_answer": "C",
      "fb": ["precipitation", "soil_moisture"],
      "latitude": 40.0,
      "longitude": -3.0
    }
    """
    lat = user_json['latitude']
    lon = user_json['longitude']
    fb_vars = user_json['fb']
    selected = user_json['selected_answer']
    correct = user_json['correct_answer']
    user_text = user_json['options'].get(selected, "Your choice")
    correct_text = user_json['options'].get(correct, "Correct choice")

    
    climate = get_climate_at_location(lat, lon)
    
    if selected == correct:
        message = f"✅ Correct! The climate at this location is {climate}.\n"
        message += f"Your selected practice:\n{user_text}\n"
    else:
        message = f"❌ Your selected practice may be suboptimal for this location.\n"
        message += f"Detected climate: {climate}\n"
        message += f"Your choice:\n{user_text}\n"
        message += f"Correct choice:\n{correct_text}\n"
    
    # Generate plot as base64
    img_base64 = provide_feedback_plot(lat, lon, data, fb_vars)
    

    
    # JSON - Frontend
    return {
        "message": message,
        "plot_base64": img_base64
    }
