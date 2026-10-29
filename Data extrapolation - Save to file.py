import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# from scipy.interpolate import CubicSpline   # ← removed
import pickle


class DataInterpolator:
    def __init__(self, filepath, usecols='AT:AW', engine='openpyxl'):
        # Initialize with values from an Excel file
        self.filepath = filepath
        self.data = pd.read_excel(filepath, usecols=usecols, engine=engine).to_numpy()
        self.time = self.data[:, 0]  # Time coords
        self.x = self.data[:, 1]     # X coords
        self.y = self.data[:, 2]     # Y coords
        self.z = self.data[:, 3]     # Z coords

    def detect_resets(self):
        # Detect points where the time values suddenly decrease
        resets = np.where(np.diff(self.time) < 0)[0] + 1
        return resets

    def split_segments(self, resets):
        # Split the data at reset points
        segments = []
        start = 0
        for reset in resets:
            segments.append((self.time[start:reset],
                             self.x[start:reset],
                             self.y[start:reset],
                             self.z[start:reset]))
            start = reset
        segments.append((self.time[start:], self.x[start:], self.y[start:], self.z[start:]))
        return segments

    @staticmethod
    def detect_large_gaps(times, gap_threshold=2):
        # Detect large time gaps in a segment
        time_diff = np.diff(times)
        large_gaps = np.where(time_diff > gap_threshold)[0]
        return large_gaps

    def split_by_gaps(self, segments):
        # Create more segments based on large gaps
        further_segments = []
        for time, x, y, z in segments:
            gap_index = self.detect_large_gaps(time)
            sub_start = 0
            for gap in gap_index:
                further_segments.append((time[sub_start:gap],
                                         x[sub_start:gap],
                                         y[sub_start:gap],
                                         z[sub_start:gap]))
                sub_start = gap
            further_segments.append((time[sub_start:], x[sub_start:], y[sub_start:], z[sub_start:]))
        return further_segments

    @staticmethod
    def filter_small_segments(segments, min_points=200):
        # Remove segments that have too few points
        return [seg for seg in segments if len(np.unique(seg[0])) >= min_points]

    # --- Spline-based interpolation removed; pass-through instead ---
    @staticmethod
    def process_segments(segments):
        """
        No interpolation: just package x,y,z at the original time stamps.
        """
        packaged = []
        for segment_index, (time, x, y, z) in enumerate(segments):
            segment_array = np.stack([x, y, z], axis=-1)
            packaged.append((time, segment_array))
            print(f"Segment {segment_index}: Length = {len(time)} (no interpolation)")
        return packaged

    # --- Spline helpers removed ---

    @staticmethod
    def plot_segment(time, data, segment_index, time_unit='s', coord_unit='m'):
        """
        Plot the original data with units on axes.
        """
        x = data[:, 0]
        y = data[:, 1]
        z = data[:, 2]

        fig, axs = plt.subplots(3, 1, figsize=(12, 8), sharex=True)

        # X
        axs[0].plot(time, x, 'b.-', label='X')
        axs[0].set_ylabel(f'X [{coord_unit}]')
        axs[0].set_title(f'Segment {segment_index} - X Coordinate')
        axs[0].legend()

        # Y
        axs[1].plot(time, y, 'g.-', label='Y')
        axs[1].set_ylabel(f'Y [{coord_unit}]')
        axs[1].set_title(f'Segment {segment_index} - Y Coordinate')
        axs[1].legend()

        # Z
        axs[2].plot(time, z, 'r.-', label='Z')
        axs[2].set_ylabel(f'Z [{coord_unit}]')
        axs[2].set_xlabel(f'Time [{time_unit}]')
        axs[2].set_title(f'Segment {segment_index} - Z Coordinate')
        axs[2].legend()

        for ax in axs:
            ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.show()


def process_files(file_list, output_file="interpolated_data_alt.pkl",
                  time_unit='s', coord_unit='m', max_plots_per_file=50):
    # Process and plot files
    all_data = {}
    for filepath in file_list:
        print(f"\nProcessing file: {filepath}")
        interpolator = DataInterpolator(filepath)

        resets = interpolator.detect_resets()
        segments = interpolator.split_segments(resets)
        final_segments = interpolator.split_by_gaps(segments)
        filtered_segments = interpolator.filter_small_segments(final_segments)
        print(f"Total final segments: {len(filtered_segments)}")

        packaged_segments = interpolator.process_segments(filtered_segments)

        file_segments = []
        for seg_idx, (time, segment_array) in enumerate(packaged_segments):
            file_segments.append({
                "segment_index": seg_idx,
                "time": time,
                "data": segment_array
            })

        #Plot data
        for seg_idx, (time_arr, data_arr) in enumerate(packaged_segments[:max_plots_per_file]):
            DataInterpolator.plot_segment(
                time_arr, data_arr, seg_idx,
                time_unit=time_unit, coord_unit=coord_unit
            )

        # all_data[filepath] = file_segments
        #
        # with open(output_file, 'wb') as f:
        #     pickle.dump(all_data, f)
        # print(f"Saved all processed data to {output_file}")


if __name__ == "__main__":

    #Files are commented out as the last use of this code was within plotting and I did not
    #Wish to slow down my laptop

    file_list = [
        "TrackData_2021-06-07_untagged 1.xlsx",
        "TrackData_2021-06-09_Yellow 8.xlsx",
        # "TrackData_2021-08-24_Brown (Rq).xlsx",
        # "TrackData_2021-08-25_Red 70.xlsx",
        # "TrackData_2021-08-26_White (R73).xlsx",
        # "TrackData_2021-08-27_Yellow 21.xlsx",
        # "TrackData_2021-09-01_Untagged 3.xlsx",
        # "TrackData_2021-09-02_Blue 83.xlsx",
        # "TrackData_2021-09-03_White 51.xlsx",
        # "TrackData_2021-09-15_Green 40.xlsx",
        # "TrackData_2021-09-16_Red 25.xlsx",
        # "TrackData_2021-09-17_Red 26.xlsx",
        # "TrackData_2021-09-22_untagged 2.xlsx",
        # "TrackData_2021-09-23_Yellow 24.xlsx",
        # "TrackData_2021-09-24_reverse 2.xlsx",
        # "TrackData_2021-10-06_Green 46.xlsx",
        # "TrackData_2021-10-07_Red 32.xlsx",
        # "TrackData_2021-10-12_Untagged.xlsx",
        # "TrackData_2021-10-13_Yellow 44.xlsx",
        # "TrackData_2021-10-14_Green 48.xlsx",
        # "TrackData_2021-10-20_Green 11.xlsx",
        # "TrackData_2021-10-27_untagged 4.xlsx",
        # "TrackData_2021-10-28_Red 33.xlsx",
        # "TrackData_2022-02-17_Red 82.xlsx",
        # "TrackData_2022-02-22_Yellow 64.xlsx",
        # "TrackData_2022-02-23_Green 53.xlsx",
        # "TrackData_2022-02-24_Reverse 2.xlsx",
        # "TrackData_2022-03-22_Red 61.xlsx",
        # "TrackData_2022-03-23_Untagged 6.xlsx",
        # "TrackData_2022-03-30_Green 56.xlsx",
        # "TrackData_2022-03-31_Yellow 66.xlsx",
        # "TrackData_2022-04-05_Untagged 7.xlsx",
        # "TrackData_2022-04-06_Red 45.xlsx",
        # "TrackData_2022-04-07_Untagged 8 (Yellow 73).xlsx",
        # "TrackData_2022-04-08_Yellow 71.xlsx",
        # "TrackData_2022-04-12_Untagged 9.xlsx",
        # "TrackData_2022-04-15_Blue 41.xlsx",
        # "TrackData_2022-04-20_Blue 65.xlsx",
        # "TrackData_2022-04-21_Untagged 10.xlsx",
        # "TrackData_2022-06-07_Untagged 11.xlsx",
        # "TrackData_2022-06-08_White 90.xlsx",
        # "TrackData_2022-06-09_Green 62.xlsx",
        # "TrackData_2022-06-14_Untagged 12.xlsx",
        # "TrackData_2022-06-16_Untagged 13.xlsx",
        # "TrackData_2022-06-17_Yellow 78.xlsx",
        # "TrackData_2022-06-22_Yellow 83.xlsx",
        # "TrackData_2022-06-23_Green 66.xlsx",
        # "TrackData_2022-06-28_Green 67.xlsx",
        # "TrackData_2022-06-29_White 95.xlsx",
        # "TrackData_2022-07-06_Blue 74.xlsx",
        # "TrackData_2022-07-07_Green 68.xlsx",
        "TrackData_2022-07-08_Yellow 85.xlsx"]
    process_files(file_list, time_unit='s', coord_unit='m', max_plots_per_file=50)
