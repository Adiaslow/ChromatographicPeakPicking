import numpy as np

def process_sequence_count_chromatogram_data(data_string):
    # Split the data string into individual measurements
    measurements = data_string.split(", ")

    # Initialize lists to store the parsed values
    times = []
    intensities = []

    # Parse each measurement
    for measurement in measurements:
        # Split each measurement into its components

        components = measurement.replace(";", ":").split(":")

        # Extract time (convert to minutes) and intensity (last value)
        time_seconds = float(components[0])
        time_minutes = time_seconds / 60.0
        intensity = float(components[2])  # Take the last value (scaled intensity)

        times.append(time_minutes)
        intensities.append(intensity)

    # Convert lists to numpy arrays
    times = np.array(times)
    intensities = np.array(intensities)

    # Sort both arrays based on times
    sort_indices = np.argsort(times)
    times_sorted = times[sort_indices]
    intensities_sorted = intensities[sort_indices]

    return times_sorted, intensities_sorted
