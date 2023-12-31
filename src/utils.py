import logging
from dataclasses import dataclass

from bs4 import BeautifulSoup
from bs4.element import Tag
from requests import RequestException
from requests.models import Response
from requests_cache import CachedSession

from constants import ENCODING, PARSER_TYPE
from exceptions import ParserFindTagException


@dataclass
class ResultWarning:
    status: str
    short_status: str
    url: str


def get_response(session: CachedSession, url: str) -> Response:
    """
    Получение ответа на get-запрос и обработка возможных исключений.
    """
    try:
        response = session.get(url)
        response.encoding = ENCODING
        return response
    except RequestException:
        logging.exception(
            f'Возникла ошибка при загрузке страницы {url}',
            stack_info=True
        )


def find_tag(soup, tag, attrs=None) -> Tag:
    """
    Поиск тега в 'супе' и вызов исключения в случае если он не найден.
    """
    searched_tag = soup.find(tag, attrs=(attrs or {}))
    if searched_tag is None:
        error_msg = f'Не найден тег {tag} {attrs}'
        logging.error(error_msg, stack_info=True)
        raise ParserFindTagException(error_msg)
    return searched_tag


def get_pep_status(session: CachedSession, url: str) -> str:
    """
    Получение статуса PEP из комментариев к описанию PEP.
    """
    status = ''
    if not url:
        return status
    response = get_response(session, url)
    pep_soup = BeautifulSoup(response.text, features=PARSER_TYPE)
    dl_div = find_tag(pep_soup, 'dl')
    dt_divs = BeautifulSoup.find_all(dl_div, 'dt')
    for dt_div in dt_divs:
        if dt_div.text == 'Status:':
            status = dt_div.find_next_sibling().string
            break
    return status
