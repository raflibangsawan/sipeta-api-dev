import mimetypes
import os

import pandas as pd


def get_filename_and_mimetype(file_path):
    head, file_name = os.path.split(file_path)
    mime_type, _ = mimetypes.guess_type(file_path)
    return file_name, mime_type


def parse_xlsx_to_string(file):
    parsed_result = ""
    read_file = pd.read_excel(file, header=None)
    row_count, column_count = read_file.shape
    for row in range(row_count):
        for column in range(column_count):
            parsed_result += str(read_file.iat[row, column])
            if column < column_count - 1:
                parsed_result += ","
        if row < row_count - 1:
            parsed_result += "\n"
    return parsed_result


def parse_xlsx_to_list_of_dict(file, column_names=None):
    parsed_result = []
    read_file = pd.read_excel(file, header=None)
    row_count, column_count = read_file.shape
    if column_names is None:
        column_names = [str(read_file.iat[0, column]) for column in range(column_count)]
    elif len(column_names) != column_count:
        raise ValueError("column_names length must be equal to column_count")
    for row in range(1, row_count):
        parsed_row = {}
        for column in range(column_count):
            parsed_row[column_names[column]] = str(read_file.iat[row, column])
        parsed_result.append(parsed_row)
    return parsed_result
