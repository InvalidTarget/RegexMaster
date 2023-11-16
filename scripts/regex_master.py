#!/home/invalidtarget/.virtualenvs/Python_Project/bin/python3
# -*- coding: utf-8 -*-

#   RegexMaster, global data downloader, using regex patterns.
#   Copyright (C) 2023 Dmitri Kuznetsov

#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.

#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program. If not, see <https://www.gnu.org/licenses/>.

# These are the import statements. The code is importing various libraries and modules that will be used later in the code.
import os
import sys
import pprint
import hashlib
import logging

import requests
import re

from user_agent import generate_navigator
from colorama import Fore, Style, init
init() # This initializes the colorama module for colored output.

# These lines define some color constants for use in the output.
# They make use of colorama for colored text output.
RED = Fore.RED + Style.BRIGHT
GREEN = Fore.GREEN + Style.BRIGHT
YELLOW = Fore.YELLOW + Style.BRIGHT

# This class is defined with the name RegexMaster.
class RegexMaster:
    # This is a method that initializes the class. It sets up logging and some initial variables.
    def __init__(self) -> None:
        super().__init__()

        self._title = GREEN + "-" * 10 + " Regex Master 1.0.0 " + "-" * 10 + "\n"

        # Setting up logging to write to a file with specific formatting.
        logging.basicConfig(
            filename="rema.log", format="%(levelname)s - %(message)s", filemode="w"
        )
        self._logger = logging.getLogger()
        self._logger.setLevel(logging.DEBUG)

        # Generating a user agent string for the requests.
        self._headers = generate_navigator()
        self._session = requests.Session()

    # This method reads links from a file and returns a list of parsed links.
    def get_links(self) -> list[str]:
        filename = "links.txt"
        try:
            with open(filename, "r") as links_file_in:
                raw_links = links_file_in.read().splitlines()

                parsed_links = list(set([link for link in raw_links if link.strip()]))

                if len(parsed_links) == 0:
                    print(f"{RED}ERROR: The file with the links is empty.")
                else:
                    self._logger.info(f"Total links found in file: {len(parsed_links)}")
                    return parsed_links

        except FileNotFoundError as fnferr:
            print(f"{RED}ERROR: {fnferr}")

        except Exception as err:
            print(f"{RED}ERROR: {err}")

        self.press_enter_to_continue()
        return None

    # This method reads patterns from a file and returns a list of parsed patterns.
    def get_patterns(self) -> list[str]:
        filename = "patterns.txt"
        try:
            with open(filename, "r") as patterns_file_in:
                raw_patterns = patterns_file_in.read().splitlines()

                parsed_patterns = list(
                    set([pattern for pattern in raw_patterns if pattern.strip()])
                )

                if len(parsed_patterns) == 0:
                    print(f"{RED}ERROR: The file with the patterns is empty.")
                else:
                    self._logger.info(
                        f"Total patterns found in file: {len(parsed_patterns)}"
                    )
                    return parsed_patterns

        except FileNotFoundError as fnferr:
            print(f"{RED}ERROR: {fnferr}")

        except Exception as err:
            print(f"{RED}ERROR: {err}")

        self.press_enter_to_continue()
        return None

    # This method sends a request to a URL and returns the HTML response.
    def get_html_site_str(self, url: str) -> requests.Response:
        self._logger.info(f"Sending requests to {url}")
        self._headers["referer"] = ""
        try:
            response = self._session.get(url, headers=self._headers)
            response.raise_for_status()

            if response.status_code == requests.codes.ok:
                self._logger.info(f"Status Code [{response.status_code}]")
                return response.text
            else:
                self._logger.error(f"Status Code [{response.status_code}]")
                return None

        except requests.exceptions.RequestException as err:
            self._logger.error(f"{err}")
            return None


    # This method applies regex patterns to HTML content and returns matching results.
    def regex_protocol(self, html_str: str, regex_patterns: str) -> list[str]:
        result = []
        for repa in regex_patterns:
            match_group = repa.split("#")[1]

            pattern = re.compile(repa.split("#")[0])

            result = re.findall(pattern, html_str)

            if len(result) == 0:
                continue
            else:
                self._logger.info("REGEX FOUND.")
                if match_group == "None":
                    return list(set([link for link in result]))
                else:
                    try:
                        match_group = int(match_group)
                    except:
                        print(
                            f"{RED}ERROR: It was not specified whether the regular expression is in a group or not.\nMatch group: {match_group}"
                        )
                        self.press_enter_to_continue()
                        continue
                    else:
                        return list(set([link[match_group - 1] for link in result]))

        else:
            self._logger.warning("REGEX NOT FOUND.")
            return result

    # The download_data method is used to download data from a list of URLs. It sets the referer header, creates a directory for downloaded data if it doesn't exist, and then iterates over the list of URLs to download the data. It logs the status of the download process and handles exceptions such as timeouts and request errors.
    def download_data(self, url_list: list[str], url_href: str) -> None:
        self._headers["referer"] = url_href

        downloads_dir = "Downloaded Data"

        if not os.path.isdir(downloads_dir):
            os.mkdir(downloads_dir)

        for link in url_list:
            self._logger.info(f"Sending requests to {link}")
            try:
                response = requests.get(link, headers=self._headers, timeout=10)
                response.raise_for_status()

                if response.status_code == requests.codes.ok:
                    bytesData = response.content
                    real_extension = "." + link.split(".")[-1]
                    filename = self.get_md5_hash(bytesData) + real_extension
                    filepath = os.path.join(downloads_dir, filename)

                    with open(filepath, "wb") as file_out:
                        file_out.write(bytesData)

                    self._logger.info(f"DATA DOWNLOADED.\n")
                else:
                    self._logger.error(f"Status Code [{response.status_code}]\n")
                    continue
            except requests.exceptions.Timeout:
                self._logger.warning(f"{err}\n")
                continue
            except requests.exceptions.RequestException as err:
                self._logger.error(f"{err}\n")
                continue

    # The show_request_headers method is a utility function to display the request headers. It prints the request headers using pprint and prompts the user to press enter to continue.
    def show_request_headers(self) -> None:
        print(self._title)

        print(f"{YELLOW}Request Headers:\n\n")
        pprint.pprint(self._headers)
        print(GREEN)
        self.press_enter_to_continue()

    # The get_md5_hash method calculates the MD5 hash of the provided bytesData and returns it as a string.
    def get_md5_hash(self, bytesData: bytes) -> str:
        md5 = hashlib.md5()
        md5.update(bytesData)
        return md5.hexdigest()

    # The press_enter_to_continue method prompts the user to press enter to continue and then clears the terminal screen.
    def press_enter_to_continue(self):
        if os.name == 'nt':  # for Windows
            input("Press Enter to continue...")
            os.system('cls')
        else:  # for Unix/Linux/Mac
            input("Press Enter to continue...")
            os.system('clear')
