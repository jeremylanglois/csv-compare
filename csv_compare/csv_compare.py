import argparse
import datetime
import logging
import os
import sys
from typing import List

import numpy as np
import pandas as pd
from pandas.errors import MergeError

logger = logging.getLogger()
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(handler)
logger.setLevel(logging.INFO)

DISCREPANCIES_OUTPUT_FILE = "discrepancies_results.csv"


class InputFile:
    def __init__(self, file_type, output_directory, input_file):
        self.type = file_type
        self.output_directory = self._create_directory_if_missing(output_directory)
        self.input_file = input_file
        self.clean_up_from_previous_comparison()

    @staticmethod
    def _create_directory_if_missing(output_directory):
        if not os.path.exists(output_directory):
            os.mkdir(output_directory)
        return output_directory

    def output_files(self):
        output_file = dict()
        output_file["extra_keys"] = f"keys_only_in_{self.type}_file.csv"
        output_file["duplicated_keys"] = f"duplicated_keys_in_{self.type}_file.csv"
        return output_file

    def clean_up_from_previous_comparison(self):
        for _, output_file in self.output_files().items():
            file_path = os.path.join(self.output_directory, output_file)
            if os.path.exists(file_path):
                os.remove(file_path)

    def load_csv_file(self, key_list, columns_to_load, index_list):

        df = pd.DataFrame()
        for chunk in pd.read_csv(
                self.input_file,
                sep=";",
                encoding="ISO-8859-1",
                na_filter=False,
                memory_map=True,
                chunksize=10 ** 5,
                dtype=str,
                usecols=columns_to_load,
        ):
            df = pd.concat([df, chunk], ignore_index=True)

        logging.debug("Index dataframe")
        for index in index_list:
            df[index] = df[index].astype("category")

        if not key_list:
            key_list = list(df)
        logging.debug("Sort dataframe")
        df.sort_values(by=key_list, inplace=True)

        return df


def _get_columns_to_load(key_list, exclusion_list, columns_to_compare_list, index_list):
    if exclusion_list:
        return (
            lambda x: x not in exclusion_list,
            [key for key in key_list if key not in exclusion_list],
            [index for index in index_list if index not in exclusion_list],
        )
    elif columns_to_compare_list:
        return (
            lambda x: x in columns_to_compare_list + key_list,
            key_list,
            [
                index
                for index in index_list
                if index in columns_to_compare_list + key_list
            ],
        )
    else:
        return lambda x: x not in [], key_list, index_list


def cleanup_previous_comparison(output_directory):
    file_path = os.path.join(output_directory, DISCREPANCIES_OUTPUT_FILE)
    if os.path.exists(file_path):
        os.remove(file_path)


def csv_compare(args):
    source_file = InputFile("source", args.output_directory, args.source_file)
    target_file = InputFile("target", args.output_directory, args.target_file)

    diff_result_file = os.path.join(args.output_directory, DISCREPANCIES_OUTPUT_FILE)

    cleanup_previous_comparison(args.output_directory)

    start_time = datetime.datetime.now()
    logging.info("START")

    columns_to_load, key_list, index_list = _get_columns_to_load(
        args.key_list,
        args.exclusion_list,
        args.columns_to_compare_list,
        args.index_list,
    )

    logging.debug("Load Source")
    source_df = source_file.load_csv_file(
        key_list, columns_to_load, index_list
    )

    logging.debug("Load Target")
    target_df = target_file.load_csv_file(
        key_list, columns_to_load, index_list
    )

    keep_common_columns(source_df, target_df)

    if target_df.equals(source_df):
        logging.info("Files are exactly similar. No output files generated.")
    else:
        discrepancies_df = find_discrepancies(
            args.comparison_method, key_list, source_df, target_df
        )

        extract_unmatched_keys(discrepancies_df, source_file.output_files(), "right_only")
        extract_unmatched_keys(discrepancies_df, target_file.output_files(), "left_only")

        header_list = [x for x in list(target_df) if x not in key_list]
        discrepancies_df, discrepancies_list = extract_file_discrepancies(discrepancies_df, header_list)

        logging.debug("Output")

        output_list = key_list + [col for x in discrepancies_list for col in _get_comparison_columns(x) if
                                  x not in key_list]

        if not discrepancies_df.empty:
            logging.info(f"{discrepancies_df.shape[0]} rows with discrepancies")
            discrepancies_df[output_list].to_csv(
                diff_result_file, sep=";", index=False
            )

    end_time = datetime.datetime.now()
    logging.info("END")
    logging.info(f"Elapsed Time: {end_time - start_time}")


def find_discrepancies(comparison_method, key_list, source_df, target_df):
    logging.info("Discrepancies found between the two files.")
    logging.debug("Merge")
    try:

        discrepancies_df = source_df.merge(
            target_df,
            how="outer",
            on=key_list,
            suffixes=["_source", "_target"],
            indicator=True,
            validate=comparison_method,
        )
    except MergeError:
        extract_duplicated_keys(
            key_list, source_df, "duplicated_keys_in_source_file.csv"
        )
        extract_duplicated_keys(
            key_list, target_df, "duplicated_keys_in_target_file.csv"
        )
        sys.exit(-1)

    logging.debug(discrepancies_df["_merge"].value_counts().to_string())
    return discrepancies_df


def keep_common_columns(source_df, target_df):
    source_columns = list(source_df)
    target_columns = list(target_df)

    source_df.drop(
        [col for col in source_columns if col not in target_columns],
        axis="columns",
        inplace=True,
    )
    target_df.drop(
        [col for col in target_columns if col not in source_columns],
        axis="columns",
        inplace=True,
    )


def extract_unmatched_keys(df, output_file, merging_indicator):
    logging.info("Extract data only in the file")
    df_source = df[(df["_merge"] == merging_indicator)]
    if not df_source.empty:
        df_source.dropna(
            axis=1, how="all"
        ).to_csv(output_file["extra_keys"], sep=";", index=False)


def extract_duplicated_keys(key_list: List[str], df: pd.DataFrame, output_file: str):
    source_duplicates = df.loc[df.duplicated(subset=key_list)]
    if not source_duplicates.empty:
        logging.info("Duplicated keys found")
        source_duplicates.drop_duplicates(subset=key_list).to_csv(
            output_file, sep=";", index=False
        )


def extract_file_discrepancies(df3, header_list):
    logging.info("Extract discrepancies between the 2 files")

    df3 = df3[(df3["_merge"] == "both")]
    df3.drop("_merge", axis="columns", inplace=True)

    discrepancies_list = []

    for item in header_list:
        col_source, col_target, col_compare = _get_comparison_columns(item)
        df3[col_compare] = df3[col_source] == df3[col_target]
        if df3[col_compare].all():
            df3.drop(columns=[col_source, col_target, col_compare], inplace=True)
        else:
            discrepancies_list.append(item)
            df3.loc[df3[col_compare], [col_source, col_target]] = np.nan
            df3[col_compare].replace([True, False], [np.nan, "diff"], inplace=True)
    return df3, discrepancies_list


def _get_comparison_columns(item: str):
    return item + "_source", item + "_target", item + "_compare"


def get_args():
    parser = argparse.ArgumentParser()
    # Positional Arguments
    parser.add_argument("source_file", help="Original file.")
    parser.add_argument("target_file", help="Modified file.")
    # Options
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Increase output verbosity."
    )
    parser.add_argument(
        "-o",
        "--output_directory",
        default=os.path.join(os.path.dirname(os.path.realpath(__file__)), "results"),
        help="Directory where the output of the comparison should be stored.",
    )
    parser.add_argument(
        "-k",
        "--key_list",
        nargs="+",
        default=[],
        help="List of keys to be used to compare both files. Value of the header of the csv file.",
    )
    parser.add_argument(
        "-e",
        "--exclusion_list",
        nargs="+",
        default=[],
        help="List of columns to exclude from comparison (blacklist). "
             "For instance, to ignore a know difference. "
             "Cannot be used in combination with columns_list option.",
    )
    parser.add_argument(
        "-c",
        "--columns_to_compare_list",
        nargs="+",
        default=[],
        help="List of columns to strictly use for comparison (whitelist). "
             "Cannot be used in combination with exclusion_list option.",
    )
    parser.add_argument(
        "-i",
        "--index_list",
        nargs="+",
        default=[],
        help="Specify a list of column which contain few different values. "
             "Used to speed up the comparison.",
    )

    parser.add_argument(
        "-m",
        "--comparison_method",
        default="one_to_one",
        choices=["one_to_one", "one_to_many", "many_to_one", "many_to_many"],
        help="Method used to compare both files.",
    )

    parser.set_defaults(func=csv_compare)

    arguments = parser.parse_args()

    if arguments.verbose:
        logger.setLevel(logging.DEBUG)

    if arguments.exclusion_list and arguments.columns_to_compare_list:
        parser.error(
            "Cannot used exclusion_list in combination with columns_to_compare_list"
        )

    return arguments


if __name__ == "__main__":
    args = get_args()
    args.func(args)
