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
import csv
from StringIO import StringIO

from starthinker.util.project import project
from starthinker.util.bigquery import bigquery_date
from starthinker.third_party.xlsx import Workbook


RE_HUMAN = re.compile('[^0-9a-zA-Z]+')
INT_LIMIT = 9223372036854775807 # defined by BigQuery 64 bit mostly ( not system )


def excel_to_rows(excel_bytes):
  book = Workbook(excel_bytes)
  # load all sheets in document
  for sheet in book:
    # load all rows from sheet
    rows = []
    for row_number, cells in sheet.rowsIter(): rows.append(map(lambda cell: cell.value or cell.formula, cells))
    yield sheet.name, rows


def csv_to_rows(csv_string):
  if isinstance(csv_string, basestring): csv_string = StringIO(csv_string)
  for row in csv.reader(csv_string, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, skipinitialspace=True, escapechar='\\'):
    yield row

def rows_to_csv(rows):
  csv_string = StringIO()
  writer = csv.writer(csv_string, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
  count = 0
  for row_number, row in enumerate(rows):
    try:
      writer.writerow(row)
      count += 1
    except Exception, e:
      print 'Error:', row_number, str(e), row
  csv_string.seek(0)  # important otherwise contents is zero
  if project.verbose: print 'CSV Rows Written:', count
  return csv_string


def rows_trim(rows):
  # find most common continous length
  histogram = {}
  prior = None
  for row in rows:
    length = len(row)
    if length != prior: histogram[length] = 1
    else: histogram[length] += 1
    prior = length
  common_length = sorted(histogram.iterkeys(), key=lambda k: histogram[k], reverse=True)[0]

  # strip any columns not in common length
  rows = [row for row in rows if len(row) == common_length]
  return rows


def rows_header_trim(rows):
  first = True
  for row in rows:
    if not first: yield row
    first = False


def column_header_sanitize(cell):
  header_sanitized = RE_HUMAN.sub('_', str(cell).title().replace('%', 'Percent')).strip('_')
  if header_sanitized[0].isdigit(): header_sanitized = '_' + header_sanitized # bigquery does not take leading digits
  return header_sanitized  


def row_header_sanitize(row):
  return [column_header_sanitize(cell) for cell in row]


def rows_header_sanitize(rows):
  first = True
  for row in rows:
    if first: 
      row = row_header_sanitize(row)
      first = False
    yield row

def rows_percent_sanitize(rows):
  for row in rows:
    yield map(lambda c: c.replace('%', '').strip(), row)


def rows_date_sanitize(rows):
  first = True
  date = None
  for row in rows:
    if first:
      # find 'Date' column if it exists
      try: date = row.index('Date')
      except ValueError: pass

    # check if data studio formatting is applied
    if date is not None:
      row[date] = 'Report_Day' if first else row[date].replace('/', '').replace('-', '')

    # return the row
    yield row

    # not first row anymore
    first = False


def rows_date_add(rows, date, header=True):
  if header:
    rows[0].insert(0, 'Report_Day')
    for row in rows[1:]: row.insert(0, bigquery_date(date))
  else:
    for row in rows: row.insert(0, bigquery_date(date))
  return rows


def rows_column_add(rows, header, value, index=None):
  first = True
  for row in rows:
    row.insert(index or len(row), header if first and header is not None else value)
    yield row
    first = False


def rows_column_delete(rows, column):
  for row in rows:
    del row[column:column+1]
    yield row


def rows_null_to_value(rows, value):
  for row in rows:
    yield map(lambda c: value if c.strip().lower() == 'null' else c, row)


def rows_re_to_value(rows, regexp, value):
  regexp = re.compile(regexp)
  for row in rows:
    yield map(lambda c: regexp.sub(value, c), row)


def rows_to_type(rows, column=None):
  for row in rows:
    for index, value in enumerate(row):
      if column is None or column == index:
        # empty values are NULL ( avoid converting zero to null )
        if isinstance(value, basestring):
          if value == '':
            row[index] = None
          # all digits less than 64 bytes are integers
          elif value.isdigit():
            v = long(value)
            if abs(v) <= INT_LIMIT : row[index] = v
          # float probably needs a byte check
          elif '.' in value:
            w, d = value.split('.', 1)
            if w.isdigit() and d.isdigit():
              row[index] = float(value)
    yield row


def rows_print(rows, row_min=0, row_max=None):
  for i, row in enumerate(rows):
    if i >= row_min and (row_max is None or i <= row_max):
      print i, row
    yield row
