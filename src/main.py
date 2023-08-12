import os
import argparse
import logging
from tqdm import tqdm
from utils import (
    find_files,
    combine_xml_files,
    read_patterns_from_codeowners,
    add_codeowners_to_xml_file,
    write_to_json,
)
import uuid


def main(args):
    logging.basicConfig(level=logging.INFO)

    # xml_files_list = "tmp_" + str(uuid.uuid4()) + ".txt"
    xml_files_list = "tmp_xml_files_list.txt"

    # find all xml files and create a txt list file
    find_files(args.xmls_path, args.files_to_merge, xml_files_list)
    file_size = os.path.getsize(xml_files_list)
    if file_size == 0:
        logging.error(f"{xml_files_list} is empty!")
        raise Exception(f"{xml_files_list} is empty!")

    # combine all xml's
    combine_xml_files(xml_files_list, args.output_file)

    # process codeowners
    if args.append_codeowners or args.codeowners_json:
        patterns = read_patterns_from_codeowners(args.codeowners_file)
        testcases_owners = add_codeowners_to_xml_file(
            args.progress_bar,
            xml_files_list,
            args.xmls_path,
            patterns,
            args.output_file,
            args.append_codeowners,
        )

    # write codeowners in json file
    if args.codeowners_json:
        logging.info(f"Write codeowners to json file ...")
        write_to_json(testcases_owners, args.codeowners_json)

    logging.info(f"Report generated: {args.output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--xmls-path", required=True, help="Full path were xmls are stored."
    )
    parser.add_argument(
        "--files-to-merge",
        default="test.xml",
        help="The name of the xml file to be found.",
    )
    parser.add_argument(
        "--output-file", default="combined.xml", help="The output file name."
    )
    parser.add_argument(
        "--codeowners-file",
        default="../../.github/CODEOWNERS",
        help="The file that contains the codeowners.",
    )
    parser.add_argument(
        "--progress-bar", action="store_true", help="Show progress bar."
    )
    parser.add_argument(
        "--append-codeowners", action="store_true", help="Append codeowners to XML."
    )
    parser.add_argument(
        "--codeowners-json",
        default="",
        help="Create a json with testcases and codeowners.",
    )
    args = parser.parse_args()
    main(args)
