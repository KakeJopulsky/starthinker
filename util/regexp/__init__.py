###########################################################################
#
#  Copyright 2017 Google Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
###########################################################################

import re
from datetime import date, datetime

def date_to_str(value):
  return value.strftime('%Y-%m-%d')


RE_YYYYMMDD = re.compile(r'\d{4}[-/_]\d{2}[-/_]\d{2}')
def parse_yyyymmdd(text):
  value = (RE_YYYYMMDD.findall(text) or [None])[0]
  return value 


RE__YYYYMMDD = re.compile(r'_?\d{4}[-/]\d{2}[-/]\d{2}')
def strip_yyymmdd(text):
  return RE__YYYYMMDD.sub('', text)


RE_URL = re.compile(r'https?://[^\s\'">]+')
def parse_url(text):
  return RE_URL.findall(text)


RE_DBM_REPORT = re.compile(r'\d{13}_report/')
def parse_dbm_report_id(download_url):
  return (RE_DBM_REPORT.findall(download_url) or [''])[0].replace('_report/', '')


RE_ALPHA_NUMERIC = re.compile('([^\s\w]|_)+')
def parse_filename(text):
  return RE_ALPHA_NUMERIC.sub('', text).lower().replace(' ', '_')
