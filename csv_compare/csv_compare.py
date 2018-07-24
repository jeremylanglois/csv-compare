import pandas as pd
import numpy as np
import datetime
import os
import logging
import argparse

logger = logging.getLogger()
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def csv_compare(args):
    source_only_file = os.path.join(args.output_directory, 'source_res.csv')
    target_only_file = os.path.join(args.output_directory, 'target_res.csv')
    diff_result_file = os.path.join(args.output_directory, 'diff_res.csv')

    start_time = datetime.datetime.now()
    logging.info('START')

    logging.debug('Load Source')
    source_df = load_csv_file(args.source_file, args.key_list, args.exclusion_list, args.index_list)

    logging.debug('Load Target')
    target_df = load_csv_file(args.target_file, args.key_list, args.exclusion_list, args.index_list)

    if target_df.equals(source_df):
        logging.info('Files are exactly similar. No output files generated.')
    else:
        header_list = [x for x in list(target_df) if x not in args.key_list]
        res_list = []
        for item in header_list:
            res_list.extend([item + '_source', item + '_target', item + '_compare'])
        output_list = args.key_list + res_list
        logging.debug('Merge')
        df3 = source_df.merge(target_df, how='outer', on=args.key_list, suffixes=['_source', '_target'], indicator=True)
        for x in df3['_merge'].value_counts().to_string().split("\n"):
            logging.debug(x)

        logging.info('Extract data only in the source file')
        df_source = df3[(df3._merge == 'left_only')]
        if df_source.empty and os.path.isfile(source_only_file):
            os.remove(source_only_file)
            logging.info('No missing data in the target file')
        else:
            df_source[[x for x in output_list if "_compare" not in x]].dropna(axis=1, how='all').to_csv(
                source_only_file, sep=',', index=False)

        logging.info('Extract data only in the target file')
        df_target = df3[(df3._merge == 'right_only')]
        if df_target.empty and os.path.isfile(target_only_file):
            os.remove(target_only_file)
            logging.info('No missing data in the source file')
        else:
            df_target[[x for x in output_list if "_compare" not in x]].dropna(axis=1, how='all').to_csv(
                target_only_file, sep=',', index=False)

        logging.info('Extract data different between the 2 files')
        df3 = extract_file_diff(df3, res_list, header_list)

        logging.debug('Output')
        if df3.empty and os.path.isfile(diff_result_file):
            os.remove(diff_result_file)
            logging.info('Data present in both file are similar')
        else:
            df3[output_list].dropna(axis=1, how='all').to_csv(diff_result_file, sep=',', index=False)

    end_time = datetime.datetime.now()
    logging.info('END')
    logging.info(f'Elapsed Time: {end_time-start_time}')


def extract_file_diff(df3, res_list, header_list):
    df3 = df3[(df3._merge == 'both')]
    logging.debug('Drop Column')
    df3 = df3.drop('_merge', 1)

    logging.debug('Compare')
    for item in header_list:
        col_source = item + '_source'
        col_target = item + '_target'
        col_compare = item + '_compare'
        df3[col_compare] = np.where(df3[col_source] == df3[col_target], 'equal', 'diff')
    logging.debug('Clean')
    for item in header_list:
        col_source = item + '_source'
        col_target = item + '_target'
        col_compare = item + '_compare'
        mask = df3[col_compare] == 'equal'
        df3.loc[mask, col_source] = np.nan
        df3.loc[mask, col_target] = np.nan
        df3.loc[mask, col_compare] = np.nan
    logging.debug('Remove similar deals')
    df3.dropna(subset=res_list, how='all', inplace=True)
    return df3


def load_csv_file(csv_file, key_list, exclusion_list, index_list):
    chunk_size = 10 ** 5
    source_list = []

    for chunk in pd.read_csv(csv_file, sep=';', encoding='ISO-8859-1', na_filter=False, memory_map=True,
                             chunksize=chunk_size, dtype=str):
        if exclusion_list:
            chunk = chunk.drop(exclusion_list, axis=1)
        source_list.append(chunk)
    df = pd.concat(source_list, ignore_index=True)
    del source_list

    logging.debug('Index dataframe')
    for index in index_list:
        df[index] = df[index].astype('category')

    if not key_list:
        key_list = list(df)
    logging.debug('Sort dataframe')
    df.sort_values(by=key_list, inplace=True)

    return df


def get_args():
    parser = argparse.ArgumentParser()
    # Positional Arguments
    parser.add_argument('source_file', help='Original file.')
    parser.add_argument('target_file', help='Modified file.')
    # Options
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Increase output verbosity.')
    parser.add_argument('-o', '--output_directory', default=os.path.dirname(os.path.realpath(__file__)),
                        help='Directory where the output of the comparison should be stored.')
    parser.add_argument('-k', '--key_list', nargs='+', default=[],
                        help='List of keys to be used to compare both files. Value of the header of the csv file.')
    parser.add_argument('-e', '--exclusion_list', nargs='+', default=[],
                        help='List of columns to exclude from comparison. For instance, to ignore a know difference.')
    parser.add_argument('-i', '--index_list', nargs='+', default=[],
                        help='Specify a list of column which contain few different values. Used to speed up the comparison.')
    parser.set_defaults(func=csv_compare)

    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()
    args.func(args)
