import os
import fnmatch
import xml.etree.ElementTree as ET
import pathspec
import logging
import json
from tqdm import tqdm

def find_path(keyword, search_path):
    for root_dir, dirs, files in os.walk(search_path):
        if keyword in root_dir or keyword in dirs or keyword in files:
            return root_dir
    return None


def find_files(directory, file_pattern, output_file):
    logging.info(f"Searching files with pattern {file_pattern} inside {directory} ...")
    with open(output_file, "w") as f:
        for root, dirs, files in os.walk(directory):
            for file in files:
                if fnmatch.fnmatch(file, file_pattern) or file == file_pattern:
                    file_path = os.path.join(root, file)
                    f.write(file_path + "\n")

    logging.info(f"Full File paths saved in: {output_file}")


def combine_xml_files(xml_files_list_file, output_file):
    logging.info("Combine all xml test reports...")
    with open(xml_files_list_file, "r") as f:
        xml_files = [line.strip() for line in f]

    main_tree = ET.parse(xml_files[0])
    main_root = main_tree.getroot()

    for xml_file in xml_files[1:]:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        for elem in root:
            main_root.append(elem)

    main_tree.write(output_file)
    logging.info(f"XML files combined in: {output_file}")


def read_patterns_from_codeowners(filename):
    patterns = {}
    with open(filename, "r") as file:
        for line in file:
            line = line.strip()
            if line.startswith("#") or not line:
                continue
            parts = line.split(maxsplit=1)
            pattern = parts[0]
            owners = parts[1].split() if len(parts) > 1 else []
            patterns[pattern] = owners

    return patterns


def closest_pattern(target_file, patterns):
    closest = None
    max_matching_dirs = 0
    spec = pathspec.PathSpec.from_lines("gitwildmatch", patterns.keys())
    # print("# target_file:"+target_file)
    for pattern in patterns.keys():
        # print("## pattern:"+pattern)
        if spec.match_file(target_file):
            pattern_dirs = pattern.split("/")
            file_dirs = target_file.split("/")
            matching_dirs = len([dir for dir in pattern_dirs if dir in file_dirs])
            if matching_dirs > max_matching_dirs:
                # print("## closest:"+pattern)
                max_matching_dirs = matching_dirs
                closest = pattern

    if closest not in target_file:
        closest = None
    return closest


def add_element_after_testcase(xml_file, keyword, append_text):
    if not os.path.isfile(xml_file) or os.path.getsize(xml_file) == 0:
        logging.error(f"File {xml_file} doesn't exist or is empty.")
        return

    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
    except ET.ParseError as e:
        logging.error(f"Failed to parse XML from file {xml_file}: {e}")
        return
    except FileNotFoundError:
        logging.error(f"File not found: {xml_file}")
        return

    for testcase in root.iter("testcase"):
        # print("try match:" + testcase.get("name") + "==" +keyword)
        if testcase.get("name") == keyword:
            # print("    #### match:" + testcase.get("name") + "==" +keyword)
            testcase.set("name", testcase.get("name") + f" (owner={append_text})")
    tree.write(xml_file)


def add_codeowners_to_xml_file(
    show_progress_bar, xml_files_list_file, xmls_out_path, patterns, output_file, append_owner_in_xml=True
):
    testcases_owners = []

    logging.info("Processing codeowners ....")
    with open(xml_files_list_file, "r") as file:
        file_lines = file.readlines()
        total_files = len(file_lines)
        if show_progress_bar:
            progress_bar = tqdm(total=total_files, desc="Processing", unit="file")

        for line in file_lines:
            target_file = line.strip()
            target_file = target_file.replace(xmls_out_path, "")
            closest = closest_pattern(target_file, patterns)
            if closest and len(patterns[closest]) > 0:
                owner = patterns[closest][1]
            else:
                owner = "Unknown"
            if not show_progress_bar:
                logging.info(f"# target_file={target_file}; closest={closest} and owner={owner}")
            testcase_name = target_file.replace("/test.xml", "")
            testcase_name = testcase_name[1:] if testcase_name.startswith("/") else testcase_name

            testcases_owners.append({"testcase_name": testcase_name, "owner": owner})

            if append_owner_in_xml:
                # append codeowner in combined xml file
                if not show_progress_bar:
                    logging.info(f"## append owner={owner} for testcase_name={testcase_name}")
                add_element_after_testcase(output_file, testcase_name, owner)

            if show_progress_bar:
                progress_bar.update(1)

        if show_progress_bar:
            progress_bar.close()

    return testcases_owners


def write_to_json(data, json_filename="testcases_owners.json"):
    with open(json_filename, "w") as f:
        json.dump(data, f, indent=4)
    logging.info(f"JSON file with testcases and codeowners: {json_filename}")
