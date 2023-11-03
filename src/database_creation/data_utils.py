import numpy as np
import ast
import csv
import pickle
import os
import json


def subset_and_unwrapp(
    df,
    subset_list,
    target_column
):

    subset_df = df.loc[:, subset_list].copy()

    subset_df[target_column] = subset_df[target_column].apply(
        lambda x: ast.literal_eval(x) if isinstance(
            x,
            str
        ) and x != 'nan' else np.nan)

    subset_df = subset_df.explode(target_column)

    subset_df = subset_df.reset_index(drop=True)

    return subset_df


def parse_overview_table(df_in):

    columns = df_in.columns.to_list()

    # Find columns that have string values representing lists
    columns_with_lists = []
    for column in df_in.columns:
        if df_in[column].apply(
            lambda x: isinstance(
                x,
                str
                ) and x.startswith(
                '['
                ) and x.endswith(
                ']')
                ).any():

            columns_with_lists.append(column)

    overview_dict = {}
    table_structure = ""

    for column in columns[1:]:
        if column in columns_with_lists:
            temp_df = subset_and_unwrapp(
                df_in,
                [columns[0], column],
                column
            )

        else:
            temp_df = df_in[[columns[0], column]]

        temp_key = "ID" + column

        overview_dict[temp_key] = temp_df

        table_text = "{table:" + temp_key + ","
        column_text = "columns:[sampleId," + column + "]};"
        entry = table_text + column_text
        table_structure += entry

    print(overview_dict.keys())

    return overview_dict, table_structure


def get_unique_value_list(sample_search_df,
                          key,
                          file_path,
                          run=False):
    if run:
        com_list = sample_search_df[key].unique()
        com_par_list = []
        for item in com_list:
            if item is not np.nan:
                python_list = ast.literal_eval(item)
                com_par_list.extend(python_list)
            else:
                com_par_list.append("NULL")

        com_par_list = list(set(com_par_list))

        if key in com_par_list:
            com_par_list.remove(key)

        # Save unique values to CSV
        with open(file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows([[value] for value in com_par_list])

        print(f"Unique values for {key} saved to", file_path)
        return com_par_list

    else:
        print(f"Skipeed for {key}")
        com_par_list = []

        with open(file_path, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                com_par_list.append(row[0])

        return com_par_list


def extract_unique_options(
        sample_search_df,
        data_path,
        run=False):

    compo_file_path = data_path + "\\composition_list.csv"
    compositions = get_unique_value_list(
        sample_search_df,
        'composition',
        compo_file_path,
        run=run)

    functions_file_path = data_path + "\\functions_list.csv"
    functions = get_unique_value_list(
        sample_search_df,
        'functions',
        functions_file_path,
        run=run)

    characterizations_file_path = data_path + "\\characterizations_list.csv"
    characterizations = get_unique_value_list(
        sample_search_df,
        'characterizations',
        characterizations_file_path,
        run=run)

    return {
        "compositions": compositions,
        "functions": functions,
        "characterizations": characterizations
    }


def load_sample_list(
        output_data_dir,
        read_sample,
        n_to_read,
        data_path
        ):
    sample_list_all_path = data_path + "\\sample_list_all.pickle"
    Json_list = os.listdir(output_data_dir)
    if read_sample:

        sample_list = []
        for i in range(0, n_to_read):
            file_path = os.path.join(
                output_data_dir,
                Json_list[i])

            with open(file_path, 'r') as file:
                sample_list.append(json.load(file))

        with open(sample_list_all_path, 'wb') as file:
            pickle.dump(sample_list, file)
    else:
        with open(sample_list_all_path, 'rb') as file:
            sample_list = pickle.load(file)

    return sample_list


def parse_dictionary(source_dictionary,
                     key,
                     new_dictionary):
    for entry in source_dictionary:
        new_dictionary[str(entry)] = source_dictionary[entry][key]


def parse_overview_raw_data(
        sample_search_df,
        overview_data_path,
        re_parse_overview=False
        ):

    overview_dict_path = overview_data_path + "\\overview_dict.pickle"
    overview_table_path = overview_data_path + "\\overview_table.pickle"
    if re_parse_overview:
        overview_dict, table_structure = parse_overview_table(sample_search_df)

        with open(overview_dict_path, 'wb') as file:
            pickle.dump(overview_dict, file)

        with open(overview_table_path, 'wb') as file:
            pickle.dump(table_structure, file)
    else:
        with open(overview_dict_path, 'rb') as file:
            overview_dict = pickle.load(file)

        with open(overview_table_path, 'rb') as file:
            table_structure = pickle.load(file)

    return overview_dict, table_structure
