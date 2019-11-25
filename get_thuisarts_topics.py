#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from functools import partial
from io import StringIO
from lxml import etree
from time import sleep
from tqdm import tqdm
from typing import Dict, List
import argparse
import os
import requests
import yaml


def print_verbose(verbose: bool, s: str, /):
    if verbose:
        print(s)


if __name__ == "__main__":
    p = argparse.ArgumentParser("Thuisarts.nl onderwerpen scraper")
    p.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    p.add_argument(
        "-d", "--dry", action="store_true", help="Dry run (do not save output)"
    )
    p.add_argument("-t", "--throttle", action="store_true", help="Throttle requests")
    args = p.parse_args()
    # override print function to only print when verbose is specified
    printv = partial(print_verbose, args.verbose)

    URL = "https://thuisarts.nl/overzicht/onderwerpen"

    printv("[1/5] Getting thuisarts onderwerpen...")
    page = requests.get(URL).text
    tree = etree.parse(StringIO(page), etree.HTMLParser())
    links = tree.xpath('//ul[@class="subject-list"]/li/a')

    # build result list
    results = [
        {
            "ID": i,
            "title": link.text,
            "link": f'https://thuisarts.nl/{link.get("href")}',
        }
        for i, link in enumerate(links)
    ]
    printv(f"[2/5] Dumping surface level results to ./thuisarts.yaml...")
    if not args.dry:
        with open("thuisarts.yaml", "w") as f:
            yaml.dump(results, f, allow_unicode=True)

    # scrape the links for each entry in the results list
    printv(f"[3/5] Scraping individual pages...")
    synonym_dict: Dict[str, List[str]] = {}
    summary_dict: Dict[int, str] = {}
    for result in tqdm(results, leave=False):
        link = result["link"]
        page = requests.get(link).text
        tree = etree.parse(StringIO(page), etree.HTMLParser())

        synonyms = tree.xpath('//div[@id="block-subjectsynonymsblock"]/div/ul/li')
        synonym_dict[result["title"]] = [s.text.strip() for s in synonyms]

        summary_points = tree.xpath(
            '//div[@class="subject-summary"]/div/ul/li/descendant-or-self::*'
        )
        summary_dict[result["ID"]] = "\n".join(s.text or "" for s in summary_points)

        if args.throttle:
            sleep(2)

    if not args.dry:
        printv(f"[4/5] Writing synonyms to ./thuisarts-synonyms.yaml...")
        with open("thuisarts-synonyms.yaml", "w") as f:
            yaml.dump(synonym_dict, f, allow_unicode=True)
        printv(f"[5/5] Writing summaries to ./thuisarts-summaries/<ID>.txt...")
        os.makedirs("./thuisarts-summaries", exist_ok=True)
        for k, v in summary_dict.items():
            with open(f"thuisarts-summaries/{k}.txt", "w") as f:
                print(v, file=f)
