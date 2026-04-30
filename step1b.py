"""
Program 2: Fall-down Location Predictor
Given the time the balloon runs out of helium, predict where it will fall.

Approach: fit a degree-2 polynomial to lat(t) and lon(t) using the
available GPS data, then evaluate at runout_time. Assumes the balloon
drops straight down when helium runs out (altitude is ignored).
"""
import csv
import numpy as np


def load_gps(path):
    """
    Load GPS data from a CSV file.

    Reads the file and extracts the time_s, latitude, and longitude
    columns into numpy arrays for numerical computation.

    Args:
        path (str): Path to the GPS CSV file.

    Returns:
        times (np.array): Array of timestamps in seconds.
        lats (np.array):  Array of latitude values.
        lons (np.array):  Array of longitude values.
    """
    times, lats, lons = [], [], []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            times.append(float(row["time_s"]))
            lats.append(float(row["latitude"]))
            lons.append(float(row["longitude"]))
    return np.array(times), np.array(lats), np.array(lons)


def predict_fall_location(gps_path, runout_time_s):
    """
    Predict the fall-down location of the balloon.

    This function should:
    1. Load the GPS data using load_gps().
    2. Use np.polyfit() to fit a degree-2 polynomial to latitude
       as a function of time.
    3. Use np.polyfit() to fit a degree-2 polynomial to longitude
       as a function of time.
    4. Use np.polyval() to evaluate both polynomials at runout_time_s
       to get the predicted latitude and longitude.

    Args:
        gps_path (str):         Path to the GPS data file.
        runout_time_s (float): The time (in seconds) when helium runs out.

    Returns:
        tuple: (predicted_latitude, predicted_longitude)
    """
    # TODO: Load GPS data
    times, lats, lons = load_gps(gps_path)

    # TODO: Fit a degree-2 polynomial for latitude over time
    lat_coeffs = np.polyfit(times, lats, 2)

    # TODO: Fit a degree-2 polynomial for longitude over time
    lon_coeffs = np.polyfit(times, lons, 2)

    # TODO: Evaluate the latitude polynomial at runout_time_s
    pred_lat = np.polyval(lat_coeffs, runout_time_s)

    # TODO: Evaluate the longitude polynomial at runout_time_s
    pred_lon = np.polyval(lon_coeffs, runout_time_s)

    return float(pred_lat), float(pred_lon)


def main():
    """
    Main function that predicts the balloon's fall-down location.

    The balloon is expected to run for 3 hours (10800 seconds).
    """
    # Path to the GPS data file
    gps_path = "gps_data.csv"

    # Balloon runout time in seconds (3 hours)
    runout_time = 10800

    # Predict the fall-down location
    lat, lon = predict_fall_location(gps_path, runout_time)

    # Print the predicted coordinates
    print(f"Predicted fall-down location at t={runout_time}s:")
    print(f"  latitude  = {lat:.6f}")
    print(f"  longitude = {lon:.6f}")


if __name__ == "__main__":
    main()