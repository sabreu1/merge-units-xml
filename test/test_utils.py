import unittest
from unittest.mock import patch, mock_open

import sys

sys.path.append("../src")

from src.utils import (
    read_patterns_from_codeowners,
    closest_pattern,
    find_files,
    combine_xml_files,
    add_element_after_testcase,
)


class TestUtils(unittest.TestCase):
    def test_read_patterns_from_codeowners(self):
        test_codeowners_content = """
# Comment line
*.py    @python-owner
/dir/   @dir-owner user2
"""
        with open("temp_codeowners", "w") as f:
            f.write(test_codeowners_content)

        expected_output = {"*.py": ["@python-owner"], "/dir/": ["@dir-owner", "user2"]}

        result = read_patterns_from_codeowners("temp_codeowners")
        self.assertEqual(result, expected_output)

    def test_closest_pattern(self):
        patterns = {
            "/dir1/scripts": ["@python-owner"],
            "/scripts": ["@test-owner"],
            "/dir/": ["@dir-owner", "user2"],
        }

        self.assertEqual(
            closest_pattern("/dir1/scripts/my_script.py", patterns), "/dir1/scripts"
        )
        self.assertEqual(closest_pattern("test/my_script.py", patterns), None)
        self.assertEqual(closest_pattern("/dir/my_folder", patterns), "/dir/")

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="test/file1.xml\ntest/file2.xml\n",
    )
    @patch("os.walk")
    def test_find_files(self, mock_walk, mock_open_file):
        mock_walk.return_value = [
            ("test", ["subdir"], ["file1.xml", "file2.xml"]),
            ("test/subdir", [], ["file3.xml"]),
        ]

        find_files("test", "file1.xml", "output.txt")

        mock_open_file.assert_called_with("output.txt", "w")
        handle = mock_open_file()
        handle.write.assert_called_with("test/file1.xml\n")


if __name__ == "__main__":
    unittest.main()
