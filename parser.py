#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Life's pathetic, have fun ("▔□▔)/hi~♡ Nasy.

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
* filename: parser.py
* Last modified time: Apr 3, 2018
* license: MIT

Parser of the crawler.

Methodology:
----------

In a nutshell, find the `selector` and parse html to string.

For `title`, `.title value`.

For `publisher`, `.hitHilite`. Sometimes, `.hitHilite` will not appear. At that
    time, the record should be droped out.

For `doi`, `div.block-record-info-source > p span ~ value`. Sometime, `doi`
    will not appear. At that time, the `doi` of the record should be `NO DOI`.

For `published`, same as `doi`'s.

For `cited`, `.large-number`.

For `abstract`, `div.title3 ~ p`.

For `keywords`, `a[title='Find more records by this author keywords']`.

For `authors`, first, we should find out all of the address. Second, parsing
    the authors and their address number is significant. Finally, combine them.

----------
There are more things in heaven and earth, Horatio, than are dreamt.
 --  From "Hamlet"
"""
import re
from typing import NamedTuple, Tuple

import bs4

RECORD = NamedTuple("RECORD", [
    ("title", str),
    ("publisher", str),
    ("doi", str),
    ("published", str),
    ("cited", str),
    ("abstract", str),
    ("keywords", str),
    ("authors", str),
])

re_author = re.compile(r"\((.+?)\)\[\s+([0-9]+).+?")
re_address = re.compile(r"\[.+?([0-9]+).+?\]\s+(.+)")


def parse_title(content: bs4.BeautifulSoup) -> str:
    """Parse the html content to get title."""
    return content.select(".title value")[0].text


def parse_publisher(content: bs4.BeautifulSoup) -> str:
    """Parse the html content to get publisher infomation."""
    return content.select(".hitHilite")[0].text


def parse_doi(content: bs4.BeautifulSoup) -> str:
    """Parse the html content to get doi infomation."""
    doi_published = content.select("div.block-record-info-source > p "
                                   "span ~ value")
    if len(doi_published) == 2:
        return doi_published[0].text
    else:
        # it may happened, somtimes.
        print(f"Warning! NO DOI for '{parse_title(content)}'")
        return "NO DOI"


def parse_published(content: bs4.BeautifulSoup) -> str:
    """Parse the html content to get the published year."""
    doi_published = content.select("div.block-record-info-source > p "
                                   "span ~ value")
    if len(doi_published) == 2:
        return doi_published[1].text
    else:
        # it may happened, somtimes. See `parse_doi`
        return doi_published[0].text


def parse_cited_num(content: bs4.BeautifulSoup) -> str:
    """Parse the html content to get cited num."""
    return content.select(".large-number")[1].text.replace(" ", "")


def parse_abstract(content: bs4.BeautifulSoup) -> str:
    """Parse the html content to get the abstract."""
    return content.select("div.title3 ~ p")[0].text


def parse_keywords(content: bs4.BeautifulSoup) -> str:
    """Parse the html content to get keywords."""
    return ",".join(
        map(lambda x: x.text,
            content.select("a[title='Find more records by "
                           "this author keywords']")))


def parse_authors(content: bs4.BeautifulSoup) -> str:
    """Parse the html content to get authors."""
    address = dict(
        map(lambda x: re_address.findall(x.text)[0],
            content.select(".fr_address_row2 a")))

    def _format_single_author(author: Tuple[str, str]) -> str:
        """Format single author and his address."""
        return "@".join((author[0], address.get(author[1], "Unknow")))

    return "::".join(
        map(_format_single_author,
            re_author.findall(
                content.select("div.block-record-info "
                               "> p ")[0].text.replace("\n", ""))))


def parse(content: bs4.BeautifulSoup) -> RECORD:
    """Parse the html content."""
    return RECORD(
        parse_title(content),
        parse_publisher(content),
        parse_doi(content),
        parse_published(content),
        parse_cited_num(content),
        parse_abstract(content),
        parse_keywords(content),
        parse_authors(content),
    )


if __name__ == '__main__':
    with open("test/test.html") as f:
        content = bs4.BeautifulSoup(f.read(), "lxml")

    assert parse(content) == RECORD(
        title =
        'Bayesian inference for generalized stochastic population growth '
        'models with application to aphids',
        publisher = 'JOURNAL OF THE ROYAL STATISTICAL SOCIETY SERIES C',
        doi = '10.1111/j.1467-9876.2009.00696.x',
        published = '2010',
        cited = '28',
        abstract =
        'We analyse the effects of various treatments on cotton aphids (Aphis '
        'gossypii). The standard analysis of count data on cotton aphids '
        'determines parameter values by assuming a deterministic growth model '
        'and combines these with the corresponding stochastic model to make '
        'predictions on population sizes, depending on treatment. Here, we '
        'use an integrated stochastic model to capture the intrinsic '
        'stochasticity, of both observed aphid counts and unobserved '
        'cumulative population size for all treatment combinations '
        'simultaneously. Unlike previous approaches, this allows us to '
        'explore explicitly and more accurately to assess treatment '
        'interactions. Markov chain Monte Carlo methods are used within a '
        'Bayesian framework to integrate over uncertainty that is associated '
        'with the unobserved cumulative population size and estimate '
        'parameters. We restrict attention to data on aphid counts in the '
        'Texas High Plains obtained for three different levels of irrigation '
        'water, nitrogen fertilizer and block, but we note that the methods '
        'that we develop can be applied to a wide range of problems in '
        'population ecology.',
        keywords =
        'Cotton aphid,Markov chain Monte Carlo methods,Markov jump process,'
        'Moment closure approximation',
        authors =
        'Gillespie, Colin S.@Univ Newcastle, Sch Math & Stat, Newcastle Upon '
        'Tyne NE1 7RU, Tyne & Wear, England')
