from enum import Enum
from pathlib import Path


class HTMLTag:
    SECTION = 'section'
    DIV = 'div'
    LI = 'li'
    A = 'a'
    H1 = 'h1'
    DL = 'dl'
    UL = 'ul'
    TABLE = 'table'
    ABBR = 'abbr'


class OutputType(str, Enum):
    PRETTY = 'pretty'
    FILE = 'file'


BASE_DIR = Path(__file__).parent
MAIN_DOC_URL = 'https://docs.python.org/3/'
PEPS_URL = 'https://peps.python.org/'
DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'
EXPECTED_STATUS = {
    'A': ('Active', 'Accepted'),
    'D': ('Deferred',),
    'F': ('Final',),
    'P': ('Provisional',),
    'R': ('Rejected',),
    'S': ('Superseded',),
    'W': ('Withdrawn',),
    '': ('Draft', 'Active'),
}

ENCODING = 'utf-8'
PARSER_TYPE = 'lxml'
# Находит фразу "Python X.X yyyyyy", где X.X - версия Python, yyyyyy - статус.
VERSION_STATUS_PATTERN = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
# Находит ссылку на архив с документацией в pdf формате
PDF_A4_PATTERN = r'.+pdf-a4\.zip$'
