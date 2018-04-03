#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Life's pathetic, have fun ("▔□▔)/hi~♡ Nasy.

Excited without bugs::

    |             *         *
    |                  .                .
    |           .
    |     *                      ,
    |                   .
    |
    |                               *
    |          |\___/|
    |          )    -(             .              '
    |         =\  -  /=
    |           )===(       *
    |          /   - \
    |          |-    |
    |         /   -   \     0.|.0
    |  NASY___\__( (__/_____(\=/)__+1s____________
    |  ______|____) )______|______|______|______|_
    |  ___|______( (____|______|______|______|____
    |  ______|____\_|______|______|______|______|_
    |  ___|______|______|______|______|______|____
    |  ______|______|______|______|______|______|_
    |  ___|______|______|______|______|______|____

* author: Nasy https://nasy.moe <Nasy>
* date: Apr 2, 2018
* email: echo bmFzeXh4QGdtYWlsLmNvbQo= | base64 -D
* filename: main.py
* Last modified time: Apr 3, 2018
* license: MIT

A crawler that crawl the data from http://apps.webofknowledge.com .

Methodology:
----------

To easily crawl it, what is the prioritized is that we need to find out a
    universal link, though it is so hard! we tried to parse the urls and found
    that it use qid and doc to portray the full result of every single paper of
    a Journal. Further, we noticed there is a useful search history list, where
    we could easily figure out our waiting-crawling paper qid and the count of
    docs.

Last but not the least, parse it and finished.

See the methodology of parser in `parser.py`

----------
There are more things in heaven and earth, Horatio, than are dreamt.
 --  From "Hamlet"
"""
import re
from multiprocessing.dummy import Pool
from parser import RECORD, parse
from typing import List, NamedTuple, Tuple

import bs4
import requests as req

# Type alias
QID = int
DOC = int
JURNAL = NamedTuple("JURNAL", [("name", str), ("count", int), ("qid", QID)])

# Jurnals
JURNAL_LIST = re.findall(r"\n\([0-9]+\)\. (.+)", """
(1). Annals of Statistics::1652
(2). Journal of the American Statistical Association::2138
(3). Journal of the Royal Statistical Society: Series B::87
(4). Biometrika::1187
(5). Biometrics::2130
(6). Journal of the Royal Statistical Society: Series A::121
(7). Econometrica::940
(8). Journal of Computational and Graphical Statistics::863
(9). Journal of Multivariate Analysis::2225
(10). Journal of the Royal Statistical Society: Series C::86
(11). Journal of Statistical Software::886
(12). Computational Statistics & Data Analysis::4027
(13). Journal of Business & Economic Statistics::699
(14). Journal of Econometrics::2086
""")
JURNALS = tuple(enumerate(map(lambda x: x.split("::"), JURNAL_LIST), 3))
# NOTE(Nasy): `3` is for my search history, change to yours.

URL = (
    "http://apps.webofknowledge.com/full_record.do?product=UA&search_mode=Gen"
    "eralSearch&qid={qid}&SID=7BTagtKnmliEPhll9jz&doc={d}#searchErrorMessage")


def jurnal2nt_jurnal(jurnal: Tuple[int, List[str]]) -> JURNAL:
    """Convert jurnal to NamedTuple JURNAL.

    Args:
        jurnal: `Tuple[int, List[str]]`, a jurnal parsed from `JURNAL_LIST`.

    Return:
        jurnal: A `JURNAL`.
    """
    return JURNAL(jurnal[1][0], int(jurnal[1][1]), jurnal[0])


def crawler_one(qid_doc: Tuple[QID, DOC]) -> RECORD:
    """Crawl one jurnal page.

    Args:
        jqid_doc: `Tuple[QID, DOC]`, a qid and a doc waiting to crawl.

    Return:
        jurnal: A `JURNAL` record.
    """
    qid, doc = qid_doc
    for _ in range(5):
        try:
            res = req.get(URL.format(qid = qid, d = doc))
            content = bs4.BeautifulSoup(res.content, "lxml")
            return parse(content)
        except IndexError:
            print(qid, doc, "!ERROR!")
    print("Finally", qid, doc, "!!ERROR!!")
    return RECORD("Error", str(qid), str(doc), "", "", "", "", "")


def crawler(jurnal: JURNAL) -> None:
    """Crawl the jurnal pages."""
    pool = Pool()
    results = pool.map(crawler_one,
                       ((jurnal.qid, i + 1) for i in range(jurnal.count)))
    pool.close()
    pool.join()
    with open("data/" + jurnal.name + ".tsv", "w") as f:
        f.write("\n".join(("\t".join(result) for result in results)))


def test_normal() -> None:
    """Test a single one normal."""
    with open(
            "./test/Journal of the Royal Statistical Society: Series C.tsv"
    ) as f, open(
            "./data/Journal of the Royal Statistical Society: Series C.tsv"
    ) as o:
        assert f.read() == o.read()
        print("Test passed")


def test_full() -> None:
    """Test a single one."""
    crawler(
        jurnal2nt_jurnal(
            (12, ['Journal of the Royal Statistical Society: Series C',
                  '86'])))
    test_normal()


def main() -> None:
    """Yoooo, the main function."""
    for jurnal in map(jurnal2nt_jurnal, JURNALS):
        print(*jurnal, sep = "\t")
        crawler(jurnal)
    test_normal()


if __name__ == '__main__':
    main()
