#!/home/invalidtarget/.virtualenvs/RegexMaster/bin/python3
# -*- coding: utf-8 -*-

#   RegexMaster, global data downloader, but you have to create the regex pattern first.
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

import os
import sys
import pprint
import hashlib
import logging

import requests
import re

from user_agent import generate_navigator
from tqdm import tqdm
from colorama import Fore, Style, init
init()

RED = Fore.RED+Style.BRIGHT
GREEN = Fore.GREEN+Style.BRIGHT
YELLOW = Fore.YELLOW+Style.BRIGHT

def press_enter_to_continue() -> None: 
	input("\nPress enter to continue...")
	os.system("clear")

class RegexMaster:
	

	# SETUP
	def __init__(self) -> None:
		super().__init__()

		self._links_to_download, self._links_line_count = self.get_links()
		self._patterns, self._patterns_line_count = self.get_patterns()

		if self._links_to_download == None or self._patterns == None: 
			sys.exit()
		else:
			self._title = GREEN+"-"*10+" Regex Master 1.0 "+"-"*10+"\n"

			logging.basicConfig(filename="rema.log", format='%(levelname)s - %(message)s', filemode='w') 
			self._logger = logging.getLogger() 
			self._logger.setLevel(logging.DEBUG) 

			self._headers = generate_navigator()
			self._session = requests.Session()	
	def main(self) -> None:
		self.show_request_headers()
		print(self._title)
		print(f"INFO: Links Found In File: {len(self._links_to_download)}")
		print(f"INFO: Line Count: {self._links_line_count}\n")
		print(f"INFO: Patterns Found In File: {len(self._patterns)}")
		print(f"INFO: Line Count: {self._patterns_line_count}")
		press_enter_to_continue()

		progressbar = tqdm(range(len(self._links_to_download)))
		progressbar.set_description("Downloading data")

		self._logger.info(f"Total links found in file: {len(self._links_to_download)}")
		self._logger.info(f"Links file line count: {self._links_line_count}")

		self._logger.info(f"Total patterns found in file: {len(self._patterns)}")
		self._logger.info(f"Patterns file line count: {self._patterns_line_count}")

		self._logger.info("Starting downloads...\n")
		
		for index in progressbar:
			html_site_str = self.get_html_site_str(url=self._links_to_download[index])

			if html_site_str == None: continue
			else:
				direct_links = self.regex_protocol(html_site_str)

				if len(direct_links) == 0: continue
				else:
					self.download_data(direct_links, self._links_to_download[index])
		else:
			progressbar.close()
			os.system("clear")
			msg = "The DOWNLOAD DATA SYSTEM has been successfully implemented."
			self._logger.info(msg)
			print(f"INFO: {msg}")
			press_enter_to_continue()
			sys.exit()


	# MAIN FUNCTIONS
	def get_links(self) -> list[str]:
		filename = "links.txt"
		try: 
			with open(filename, "r") as links_file_in:
				raw_links = links_file_in.read().splitlines()
				
				parsed_links = [link for link in raw_links if link.strip()]
		
				if len(parsed_links) == 0:
					print(f"{RED}ERROR: The file with the links is empty.") 
				else: 
					return list(set(parsed_links)), len(raw_links)

		except FileNotFoundError as fnferr:
			print(f"{RED}ERROR: {fnferr}")

		except Exception as err:
			print(f"{RED}ERROR: {err}")
			
		press_enter_to_continue()
		return None
	def get_patterns(self) -> list[tuple]:
		filename = "patterns.txt"
		try: 
			with open(filename, "r") as patterns_file_in:
				raw_patterns = patterns_file_in.read().splitlines()
				
				parsed_patterns = list(set([pattern for pattern in raw_patterns if pattern.strip()]))
				
				if len(parsed_patterns) == 0:
					print(f"{RED}ERROR: The file with the patterns is empty.")
				else:
					return parsed_patterns, len(raw_patterns)

		except FileNotFoundError as fnferr:
			print(f"{RED}ERROR: {fnferr}")

		except Exception as err:
			print(f"{RED}ERROR: {err}")
			
		press_enter_to_continue()
		return None


	# WEB SCRAPING
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
	def regex_protocol(self, html_str) -> list[str]:
		result = []
		for regex in self._patterns:
			pattern = re.compile(regex)
			result = re.findall(pattern, html_str)

			if len(result) == 0: 
				continue
			else: 
				self._logger.info("REGEX FOUND.")
				return list(set([link for link in result]))
		else: 
			self._logger.warning("REGEX NOT FOUND.")
			return result
	def download_data(self, url_list: list[str], href: str) -> None:
		self._headers["referer"] = href
		downloads_dir = "Downloaded Data"
		if not os.path.isdir(downloads_dir): os.mkdir(downloads_dir)

		for link in url_list:
			self._logger.info(f"Sending requests to {link}")
			try:
				response = requests.get(link, headers=self._headers)
				response.raise_for_status()

				if response.status_code == requests.codes.ok:
					self._logger.info(f"DATA DOWNLOADED.\n")
					
					bytesData = response.content
					real_extension = "."+link.split(".")[-1]
					filename = self.get_md5_hash(bytesData)+real_extension
					filepath = os.path.join(downloads_dir, filename)

					with open(filepath, "wb") as file_out:
						file_out.write(bytesData)

				else:
					self._logger.error(f"Status Code [{response.status_code}]\n")
					continue

			except requests.exceptions.RequestException as err:
				self._logger.error(f"{err}\n")
				continue


	# UTILS 
	def show_request_headers(self) -> None: 
		print(self._title)

		print(f"{YELLOW}Request Headers:\n\n")
		pprint.pprint(self._headers)
		print(GREEN)
		press_enter_to_continue()
	def get_md5_hash(self, bytesData: bytes) -> str:
		md5 = hashlib.md5()
		md5.update(bytesData)
		return md5.hexdigest()


if __name__ == "__main__":
	regexMaster = RegexMaster()
	regexMaster.main()
	
	
	
	
