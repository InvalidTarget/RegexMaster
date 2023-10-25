#!/home/invalidtarget/.virtualenvs/Python_Project/bin/python3
# -*- coding: utf-8 -*-

#   RegexMaster, a global data downloader using regex patterns.
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
from tqdm import tqdm
from regex_master import RegexMaster

def main():
	rema = RegexMaster()
	rema.show_request_headers()
	
	_links_to_download = rema.get_links()

	if _links_to_download == None:
		sys.exit()
	else:
		_regex_patterns = rema.get_patterns()
		if _regex_patterns == None:
			sys.exit()
		else:
			print(rema._title)
			print(f"INFO: Total LINKS found in file: {len(_links_to_download)}\n")
			print(f"INFO: Total PATTERNS found in file: {len(_regex_patterns)}")
			rema.press_enter_to_continue()

			rema._logger.info("Starting downloads...\n")
			
			progressbar = tqdm(range(len(_links_to_download)))
			progressbar.set_description("Downloading Data")

			for index in progressbar:
				html_site_str = rema.get_html_site_str(url=_links_to_download[index])

				if html_site_str == None: continue
				else: 
					direct_links = rema.regex_protocol(html_site_str, _regex_patterns)

					if len(direct_links) == 0: continue
					else:
						rema.download_data(
							url_list=direct_links, 
							url_href=_links_to_download[index])
			else:
				progressbar.close()
				os.system("clear")
				msg = "The DOWNLOAD DATA SYSTEM has been successfully implemented."
				rema._logger.info(msg)
				print(f"INFO: {msg}")
				rema.press_enter_to_continue()
				sys.exit()


if __name__ == "__main__":
	main()