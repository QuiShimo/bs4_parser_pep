import logging
import re
from collections import defaultdict
from typing import List, Optional, Tuple
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup
from requests_cache import CachedSession
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import (
    BASE_DIR, EXPECTED_STATUS, MAIN_DOC_URL, PEPS_URL, PARSER_TYPE, HTMLTag,
    VERSION_STATUS_PATTERN, PDF_A4_PATTERN
)
from exceptions import ParserFindTagException
from outputs import control_output
from utils import ResultWarning, get_pep_status, get_response, find_tag


def whats_new(session: CachedSession) -> Optional[List[Tuple]]:
    """
    Парсинг страниц с описанием обновлений в версиях Python.
    """
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    response = get_response(session, whats_new_url)
    if response is None:
        return
    logging.info('Parsing news started')
    soup = BeautifulSoup(response.text, features=PARSER_TYPE)
    main_div = find_tag(soup, HTMLTag.SECTION, {'id': 'what-s-new-in-python'})
    div_with_ul = find_tag(main_div, HTMLTag.DIV, {'class': 'toctree-wrapper'})
    section_by_python = div_with_ul.find_all(
        HTMLTag.LI, attrs={'class': 'toctree-l1'}
    )
    result = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    for section in tqdm(section_by_python):
        version_a_tag = section.find(HTMLTag.A)
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)
        response = get_response(session, version_link)
        if response is None:
            continue
        soup = BeautifulSoup(response.text, features=PARSER_TYPE)
        h1 = find_tag(soup, HTMLTag.H1)
        dl = find_tag(soup, HTMLTag.DL)
        result.append((
            version_link,
            h1.text.strip().replace('\n', ' '),
            dl.text.strip().replace('\n', ' ')
        ))
    logging.info('Parsing news finished')
    return result


def latest_versions(session: CachedSession) -> Optional[List[Tuple]]:
    """
    Парсинг информации по актуальным версиям Python.
    """
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return
    logging.info('Getting latest version started')
    soup = BeautifulSoup(response.text, features=PARSER_TYPE)
    sidebar = find_tag(soup, HTMLTag.DIV, {'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all(HTMLTag.UL)
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all(HTMLTag.A)
            break
    else:
        raise ParserFindTagException('Found nothing')
    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    for a_tag in tqdm(a_tags):
        link = a_tag['href']
        text_match = re.search(VERSION_STATUS_PATTERN, a_tag.text)
        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append((link, version, status))
    logging.info('Getting latest version finished')
    return results


def download(session: CachedSession) -> None:
    """
    Скачивание zip-архива с документацией актуальной версии Python.
    """
    download_url = urljoin(MAIN_DOC_URL, 'download.html')
    response = get_response(session, download_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features=PARSER_TYPE)
    table_tag = find_tag(soup, HTMLTag.TABLE, {'class': 'docutils'})
    pdf_a4_tag = table_tag.find(
        HTMLTag.A, {'href': re.compile(PDF_A4_PATTERN)}
    )
    pdf_a4_link = pdf_a4_tag['href']
    archive_url = urljoin(download_url, pdf_a4_link)
    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename
    response = session.get(archive_url)
    with open(archive_path, 'wb') as f:
        f.write(response.content)
    logging.info(f'Архив был загружен и сохранен: {archive_path}')


def pep(session: CachedSession) -> Optional[List[Tuple]]:
    """
    Парсинг информации по статусам Python Enhancement Proposals.
    """
    response = get_response(session, PEPS_URL)
    if response is None:
        return
    logging.info('Parsing PEP statuses started')
    results, warnings = defaultdict(int), []
    soup = BeautifulSoup(response.text, features=PARSER_TYPE)
    section_div = find_tag(soup, HTMLTag.SECTION, {'id': 'numerical-index'})
    tr_divs = BeautifulSoup.find_all(section_div, 'tr')
    for tr_div in tqdm(tr_divs[1:]):
        abbr_div = find_tag(tr_div, HTMLTag.ABBR)
        short_status = abbr_div.text[1:]
        a_div = find_tag(
            tr_div,
            HTMLTag.A,
            {'class': 'pep reference internal'}
        )
        short_url = a_div.attrs.get('href', '')
        url = urljoin(PEPS_URL, short_url)
        status = get_pep_status(session, url)
        results[status] += 1
        try:
            if short_status and status not in EXPECTED_STATUS[short_status]:
                warnings.append(
                    ResultWarning(
                        status=status,
                        short_status=short_status,
                        url=url
                    )
                )
        except KeyError as e:
            logging.error(f'В словаре EXPECTED_STATUS не '
                          f'найден ключ {short_status}: {e}')
    logging.info('Parsing PEP statuses finished')
    if warnings:
        logging.warning('Несовпадающие статусы:')
        for warning in warnings:
            logging.warning(
                '%s\nСтатус в карточке: %s\nОжидаемые статусы: %s',
                warning.url,
                warning.status,
                list(EXPECTED_STATUS[warning.short_status])
            )
    result = [('Статус', 'Количество')]
    for status, count in results.items():
        result.append((status, count))
    result.append(('Итого', len(tr_divs) - 1))
    return result


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep
}


def main():
    configure_logging()
    logging.info('Parser started')
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info('command line arguments: %s', args)
    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()
    parser_mode = args.mode
    func = MODE_TO_FUNCTION[parser_mode]
    results = func(session)
    if results is not None:
        control_output(results, args)
    logging.info('All jobs done')


if __name__ == '__main__':
    main()
