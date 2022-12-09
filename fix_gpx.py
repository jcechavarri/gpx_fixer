from typing import Any, List, Tuple, Union
from dateutil import parser
from datetime import datetime, timedelta


def get_index_range(tag_name: str, line: str) -> Union[None, Tuple[int, int]]:
    """
    It takes a line of text and a tag name, and returns the start and end indices of
    the text between the tags

    :param tag_name: The name of the tag you want to extract the text from
    :type tag_name: str
    :param line: The line of text we're parsing
    :type line: str
    :return: A tuple of the start and end index of the tag.
    """
    open_tag = f"<{tag_name}>"
    close_tag = f"</{tag_name}>"

    # Sanity check
    if open_tag not in line:
        return None

    start_idx = line.find(open_tag) + len(open_tag)
    close_idx = line.find(close_tag)
    return start_idx, close_idx


def get_tag_value(tag: str, line: str) -> Union[None, str]:
    if indexes := get_index_range(tag, line):
        return line[indexes[0] : indexes[1]]


def find_tag_value(tag: str, lines: List[str]) -> Union[None, str]:
    """
    It returns the value inside the tag in the line.

    :param line: str - the line to search for the tag
    :type line: str
    :param tag: the tag you want to get the value of
    :type tag: str
    :return: The value of the tag.
    """
    return next((value for line in lines if (value := get_tag_value(tag, line))), None)


def d2s(date: datetime) -> str:
    return date.strftime("%Y-%m-%dT%H:%M:%S.000Z")


def remove_data_tag(tag: str, line: str):
    start, end = get_index_range(tag, line)
    start -= len(tag) + 2
    end += len(tag) + 3
    return line[:start] + line[end:]


def replace_data_tag(tag: str, line: str, new_value: str):
    start, end = get_index_range(tag, line)
    return line[:start] + new_value + line[end:]


def fix_file(lines: List[str]):
    metadata = find_tag_value("metadata", lines)
    # export time, defines failing datestimes
    saved_time = get_tag_value("time", metadata)
    # Last index with useful data
    last_idx = (
        next(i for i, line in reversed(list(enumerate(lines))) if saved_time in line)
        + 1
    )
    start_datetime_str = get_tag_value("time", lines[last_idx])

    new_lines = []
    curr_time = parser.parse(start_datetime_str)
    for i, line in enumerate(lines):
        if i <= last_idx:
            if "trkpt" in line:
                new_line = remove_data_tag("ele", line)
                new_line = replace_data_tag("time", new_line, d2s(curr_time))
                curr_time += timedelta(seconds=1)
                new_lines.append(new_line)
            else:
                new_lines.append(line)
        elif not "trkpt" in line:
            new_lines.append(line)

    return new_lines


if __name__ == "__main__":
    path = "20221208Mountain hike.gpx"
    with open(path, "r") as file:
        lines = file.readlines()

    new_lines = fix_file(lines)

    print("".join(new_lines))
    with open("new_gpx.gpx", "w") as file:
        file.write("".join(new_lines))
