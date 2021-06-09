"""
    The datetime_based  module contains all the features of the library
    that calculates several features based on the DateTime provided in
    the data. It is to be noted that most of the functions in this module
    calculate the features and then add the results to an entirely new
    column with a new column header. It is to be also noted that a lot of
    these features are inspired from the PyMove library and we are
    crediting the PyMove creators with them.

    @authors Yaksh J Haranwala, Salman Haidri
    @date 22 May, 2021
    @version 1.0
    @credits PyMove creators
"""
import itertools
import multiprocessing
from typing import Optional, Text

import numpy as np
import pandas as pd

from core.TrajectoryDF import NumPandasTraj
from features.helper_functions import Helpers as helpers
from utilities import constants as const


class TemporalFeatures:
    # @staticmethod
    # def create_date_column_alt(dataframe: NumPandasTraj):
    #     """
    #         Create a Date column in the dataframe given.
    #
    #         Parameters
    #         ----------
    #             dataframe: core.TrajectoryDF.NumPandasTraj
    #                 The NumPandasTraj on which the creation of date column is to be done.
    #
    #         Returns
    #         -------
    #             core.TrajectoryDF.NumPandasTraj
    #                 The dataframe containing the resultant column.
    #     """
    #     # Split the entire data set into chunks of 100000 rows each
    #     # so that we can work on each separate part in parallel.
    #     split_list = []
    #     for i in range(0, len(dataframe), 100001):
    #         split_list.append(dataframe.reset_index(drop=False).iloc[i:i + 100000])
    #
    #     method_pool = multiprocessing.Pool(len(split_list))  # Create a pool of processes.
    #
    #     # Now run the date helper method in parallel with the dataframes in split_list
    #     # and the new dataframes with date columns are stored in the variable result which is of type Mapper.
    #     result = method_pool.map(helpers._date_helper, split_list)
    #
    #     ans = pd.concat(result)  # Merge all the smaller chunks together.
    #
    #     # Now depending on the value of inplace, return the required data structure.
    #     return NumPandasTraj(ans, const.LAT, const.LONG, const.DateTime, const.TRAJECTORY_ID)

    @staticmethod
    def create_time_column(dataframe: NumPandasTraj):
        """
            From the DateTime column already present in the data, extract only the time
            and then add another column containing just the time.
            Parameters
            ----------
                dataframe: NumPandasTraj
                    The DaskTrajectoryDF on which the creation of the time column is to be done.

            Returns
            -------
                core.TrajectoryDF.NumPandasTraj
                    The dataframe containing the resultant column.

        """
        df_split_list = []  # A list for storing the split dataframes.

        # Now, we are going to split the dataframes into chunks of 75000 rows each.
        # This is done in order to create processes later and then feed each process
        # a separate dataframe and calculate the results in parallel.
        for i in range(0, len(dataframe), 75000):
            df_split_list.append(dataframe.reset_index(drop=False).iloc[i:i + 75000])

        # Now, create a pool of processes which has a number of processes
        # equal to the number of smaller chunks of the original dataframe.
        # Then, calculate the result on each separate part in parallel and store it in
        # the result variable which is of type Mapper.
        pool = multiprocessing.Pool(len(df_split_list))
        result = pool.map(helpers._time_helper, df_split_list)

        time_containing_df = pd.concat(result)  # Now join all the smaller pieces together.

        # Now check whether the user wants the result applied to the original dataframe or
        # wants a separate new dataframe. If the user wants a separate new dataframe, then
        # a pandas dataframe is returned instead of NumTrajectoryDF.
        return NumPandasTraj(time_containing_df, const.LAT, const.LONG, const.DateTime, const.TRAJECTORY_ID)

    @staticmethod
    def create_day_of_week_column(dataframe: NumPandasTraj):
        """
            Create a column called Day_Of_Week which contains the day of the week
            on which the trajectory point is recorded. This is calculated on the basis
            of timestamp recorded in the data.

            Parameters
            ----------
                dataframe: NumPandasTraj
                    The dataframe containing the entire data on which the operation is to be performed

            Returns
            -------
                core.TrajectoryDF.NumPandasTraj
                    The dataframe containing the resultant column.
        """
        df = dataframe.reset_index()
        # First, create a list containing all the ids of the data and then further divide that
        # list items and split it into sub-lists of 100 ids each if there are more than 100 ids.
        ids_ = df[const.TRAJECTORY_ID].value_counts(ascending=True).keys().to_list()

        # Get the ideal number of IDs by which the dataframe is to be split.
        split_factor = helpers._get_partition_size(len(ids_))
        ids_ = [ids_[i: i + split_factor] for i in range(0, len(ids_), split_factor)]

        df_chunks = []

        # Now split the dataframes based on set of Trajectory ids.
        # As of now, each smaller chunk is supposed to have data of 100
        # trajectory IDs max
        for i in range(len(ids_)):
            df_chunks.append(df.loc[df[const.TRAJECTORY_ID].isin(ids_[i])])

        # Now lets create a pool of processes which will then create processes equal to
        # the number of smaller chunks of the original dataframe and will calculate
        # the result on each of the smaller chunk.
        pool_of_processes = multiprocessing.Pool(len(chunk_list))
        results = pool_of_processes.map(helpers._day_of_week_helper, chunk_list)

        final_df = pd.concat(results)
        return NumPandasTraj(final_df, const.LAT, const.LONG, const.DateTime, const.TRAJECTORY_ID)

    @staticmethod
    def create_weekend_indicator_column(dataframe: NumPandasTraj):
        """
            Create a column called Weekend which indicates whether the point data is collected
            on either a Saturday or a Sunday.

            Parameters
            ----------
                dataframe: NumPandasTraj
                    The dataframe on which the operation is to be performed.

            Returns
            -------
                core.TrajectoryDF.NumPandasTraj
                    The dataframe containing the resultant column if inplace.

        """
        df = dataframe.reset_index()
        # First, create a list containing all the ids of the data and then further divide that
        # list items and split it into sub-lists of 100 ids each if there are more than 100 ids.
        ids_ = df[const.TRAJECTORY_ID].value_counts(ascending=True).keys().to_list()

        # Get the ideal number of IDs by which the dataframe is to be split.
        split_factor = helpers._get_partition_size(len(ids_))
        ids_ = [ids_[i: i + split_factor] for i in range(0, len(ids_), split_factor)]

        df_chunks = []

        # Now split the dataframes based on set of Trajectory ids.
        # As of now, each smaller chunk is supposed to have data of 100
        # trajectory IDs max
        for i in range(len(ids_)):
            df_chunks.append(df.loc[df[const.TRAJECTORY_ID].isin(ids_[i])])

        # Now lets create a pool of processes and run the weekend calculator function
        # on all the smaller parts of the original dataframe and store their results.
        mp_pool = multiprocessing.Pool(len(parts))
        results = mp_pool.map(helpers._weekend_helper, parts)

        # Now, lets merge all the smaller parts together and then return the results based on
        # the value of the inplace parameter.
        final_df = pd.concat(results)
        return NumPandasTraj(final_df, const.LAT, const.LONG, const.DateTime, const.TRAJECTORY_ID)

    @staticmethod
    def create_time_of_day_column(dataframe: NumPandasTraj):
        """
            Create a Time_Of_Day column in the dataframe which indicates at what time of the
            day was the point data captured.
            Note: The divisions of the day based on the time are provided in the utilities.constants module.

            Parameters
            ----------
                dataframe: NumPandasTraj
                    The dataframe on which the calculation is to be done.

            Returns
            -------
                core.TrajectoryDF.NumPandasTraj
                    The dataframe containing the resultant column.

        """
        df = dataframe.reset_index()
        # First, create a list containing all the ids of the data and then further divide that
        # list items and split it into sub-lists of 100 ids each if there are more than 100 ids.
        ids_ = df[const.TRAJECTORY_ID].value_counts(ascending=True).keys().to_list()

        # Get the ideal number of IDs by which the dataframe is to be split.
        split_factor = helpers._get_partition_size(len(ids_))
        ids_ = [ids_[i: i + split_factor] for i in range(0, len(ids_), split_factor)]

        df_chunks = []

        # Now split the dataframes based on set of Trajectory ids.
        # As of now, each smaller chunk is supposed to have data of 100
        # trajectory IDs max
        for i in range(len(ids_)):
            df_chunks.append(df.loc[df[const.TRAJECTORY_ID].isin(ids_[i])])

        # Now lets create a pool of processes and run the weekend calculator function
        # on all the smaller parts of the original dataframe and store their results.
        multi_pool = multiprocessing.Pool(len(divisions))
        results = multi_pool.map(helpers._time_of_day_helper, divisions)

        # Now, lets merge all the smaller parts together and then return the results based on
        # the value of the inplace parameter.
        final_df = pd.concat(results)
        return NumPandasTraj(final_df, const.LAT, const.LONG, const.DateTime, const.TRAJECTORY_ID)

    @staticmethod
    def get_traj_duration(dataframe: NumPandasTraj, traj_id: Optional[Text] = None):
        """
            Accessor method for the duration of a trajectory specified by the user.
            Note: If no trajectory ID is given by the user, then the duration of the entire
                  data set is given i.e., the difference between the max time in the dataset
                  and the min time in the dataset.

            Parameters
            ----------
                dataframe: core.TrajectoryDF.NumPandasTraj
                    The dataframe containing the resultant column if inplace is True.
                traj_id: Optional[Text]
                    The trajectory id for which the duration is required.

            Returns
            -------
                pandas.TimeDelta
                    The trajectory duration.
        """
        if traj_id is None:
            return dataframe.reset_index()['DateTime'].max() - dataframe.reset_index()['DateTime'].min()
        else:
            small = dataframe.reset_index().loc[
                dataframe.reset_index()[const.TRAJECTORY_ID] == traj_id, [const.DateTime]]
            if len(small) == 0:
                return f"No {traj_id} exists in the given data. Please try again."
            else:
                return small.max() - small.min()

    @staticmethod
    def get_start_time(dataframe: NumPandasTraj, traj_id: Optional[Text] = None):
        """
            Get the starting time of the trajectory.
            NOTE: If the trajectory ID is not specified by the user, then by default,
                  the starting times of all the trajectory IDs in the data are
                  returned.

            Parameters
            ----------
                dataframe: NumPandasTraj
                    The dataframe on which the operations are to be performed.
                traj_id: Optional[Text]
                    The trajectory for which the start time is required.

            Returns
            -------
                pandas.DateTime:
                    The start time of a single trajectory.
                pandas.core.dataframe.DataFrame
                    Pandas dataframe containing the start time of all the trajectories
                    present in the data when the user hasn't asked for a particular
                    trajectory's start time.
        """
        dataframe = dataframe.reset_index()
        if traj_id is None:
            # First, create a list containing all the ids of the data and then further divide that
            # list items and split it into sub-lists of 100 ids each if there are more than 100 ids.
            ids_ = dataframe[const.TRAJECTORY_ID].value_counts(ascending=True).keys().to_list()

            # Get the ideal number of IDs by which the dataframe is to be split.
            split_factor = helpers._get_partition_size(len(ids_))
            ids_ = [ids_[i: i + split_factor] for i in range(0, len(ids_), split_factor)]

            # Now, create a multiprocessing pool and then run processes in parallel
            # which calculate the start times for a smaller set of IDs only.
            mp_pool = multiprocessing.Pool(len(ids_))
            results = mp_pool.starmap(helpers._start_time_helper, zip(itertools.repeat(dataframe), ids_))

            # Concatenate all the smaller dataframes and return the answer.
            results = pd.concat(results).sort_values(const.TRAJECTORY_ID)
            return results
        else:
            filt = dataframe.loc[dataframe[const.TRAJECTORY_ID] == traj_id]
            filt_two = filt.loc[filt[const.DateTime] == filt[const.DateTime].min()]
            return filt_two[const.DateTime].iloc[0]

    @staticmethod
    def get_end_time(dataframe: NumPandasTraj, traj_id: Optional[Text] = None):
        """
            Get the ending time of the trajectory.
            NOTE: If the trajectory ID is not specified by the user, then by default,
                  the ending times of all the trajectory IDs in the data are
                  returned.

            Parameters
            ----------
                dataframe: NumPandasTraj
                    The dataframe on which the operations are to be performed.
                traj_id: Optional[Text]
                    The trajectory for which the end time is required.

            Returns
            -------
                pandas.DateTime:
                    The end time of a single trajectory.
                pandas.core.dataframe.DataFrame
                    Pandas dataframe containing the end time of all the trajectories
                    present in the data when the user hasn't asked for a particular
                    trajectory's end time.
        """
        dataframe = dataframe.reset_index()
        if traj_id is None:
            # First, create a list containing all the ids of the data and then further divide that
            # list items and split it into sub-lists of 100 ids each if there are more than 100 ids.
            ids_ = dataframe[const.TRAJECTORY_ID].value_counts(ascending=True).keys().to_list()

            # Get the ideal number of IDs by which the dataframe is to be split.
            split_factor = helpers._get_partition_size(len(ids_))
            ids_ = [ids_[i: i + split_factor] for i in range(0, len(ids_), split_factor)]

            # Now, create a multiprocessing pool and then run processes in parallel
            # which calculate the end times for a smaller set of IDs only.
            mp_pool = multiprocessing.Pool(len(ids_))
            results = mp_pool.starmap(helpers._end_time_helper, zip(itertools.repeat(dataframe), ids_))

            # Concatenate all the smaller dataframes and return the answer.
            results = pd.concat(results).sort_values(const.TRAJECTORY_ID)
            return results
        else:
            filt = dataframe.loc[dataframe[const.TRAJECTORY_ID] == traj_id]
            filt_two = filt.loc[filt[const.DateTime] == filt[const.DateTime].max()]
            return filt_two[const.DateTime].iloc[0]

    @staticmethod
    def convert_timezone(dataframe: NumPandasTraj, from_timezone, target_timezone):
        pass
