#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of the python-chess library.
# Copyright (C) 2012-2016 Niklas Fiekas <niklas.fiekas@backscattering.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function

import chess
import chess.uci
import chess.variant
import time
import textwrap
import argparse
import itertools
import logging
import sys


def test_epd(engine, epd, VariantBoard, movetime):
    position = VariantBoard()
    epd_info = position.set_epd(epd)
    epd_string = "%s" % epd_info.get("id", position.fen())
    if "am" in epd_info:
        epd_string = "%s (avoid %s)" % (epd_string, " and ".join(position.san(am) for am in epd_info["am"]))
    if "bm" in epd_info:
        epd_string = "%s (expect %s)" % (epd_string, " or ".join(position.san(bm) for bm in epd_info["bm"]))

    engine.ucinewgame()
    engine.setoption({"UCI_Variant": VariantBoard.uci_variant})
    engine.position(position)

    enginemove, pondermove = engine.go(movetime=movetime)

    if "am" in epd_info and enginemove in epd_info["am"]:
        print("%s: %s | +0" % (epd_string, position.san(enginemove)))
        return 0.0
    elif "bm" in epd_info and not enginemove in epd_info["bm"]:
        print("%s: %s | +0" % (epd_string, position.san(enginemove)))
        return 0.0
    else:
        print("%s: %s | +1" % (epd_string, position.san(enginemove)))
        return 1.0


def test_epd_with_fractional_scores(engine, epd, VariantBoard, movetime):
    info_handler = chess.uci.InfoHandler()
    engine.info_handlers.append(info_handler)

    position = VariantBoard()
    epd_info = position.set_epd(epd)
    epd_string = "%s" % epd_info.get("id", position.fen())
    if "am" in epd_info:
        epd_string = "%s (avoid %s)" % (epd_string, " and ".join(position.san(am) for am in epd_info["am"]))
    if "bm" in epd_info:
        epd_string = "%s (expect %s)" % (epd_string, " or ".join(position.san(bm) for bm in epd_info["bm"]))

    engine.ucinewgame()
    engine.setoption({"UCI_Variant": VariantBoard.uci_variant})
    engine.position(position)

    # Search in background
    search = engine.go(infinite=True, async_callback=True)

    score = 0.0

    print("%s:" % epd_string, end=" ")
    sys.stdout.flush()

    for step in range(0, 3):
        time.sleep(movetime / 4000.0)

        # Assess the current principal variation.
        with info_handler as info:
            if 1 in info["pv"] and len(info["pv"][1]) >= 1:
                move = info["pv"][1][0]
                print("(%s)" % position.san(move), end=" ")
                sys.stdout.flush()
                if "am" in epd_info and move in epd_info["am"]:
                    continue #fail
                elif "bm" in epd_info and not move in epd_info["bm"]:
                    continue #fail
                else:
                     score = 1.0 / (4 - step)
            else:
                print("(no pv)", end=" ")
                sys.stdout.flush()

    # Assess the final best move by the engine.
    time.sleep(movetime / 4000.0)
    engine.stop()
    enginemove, pondermove = search.result()
    if "am" in epd_info and enginemove in epd_info["am"]:
        pass #fail
    elif "bm" in epd_info and not enginemove in epd_info["bm"]:
        pass #fail
    else:
         score = 1.0

    print("%s | +%g" % (position.san(enginemove), score))

    engine.info_handlers.remove(info_handler)
    return score


if __name__ == "__main__":
    # Parse command line arguments.
    parser = argparse.ArgumentParser(description="Run an EPD test suite with an UCI engine.")
    parser.add_argument("-e", "--engine", required=True,
        help="The UCI engine under test.")
    parser.add_argument("epd", nargs="+", type=argparse.FileType("r"),
        help="EPD test suite(s).")
    parser.add_argument("-v", "--variant", default="standard",
        help="Use a non-standard chess variant.")
    parser.add_argument("-t", "--movetime", default=1000, type=int,
        help="Time to move in milliseconds.")
    parser.add_argument("-s", "--simple", dest="test_epd", action="store_const",
        default=test_epd_with_fractional_scores,
        const=test_epd,
        help="Run in simple mode without fractional scores.")
    parser.add_argument("-d", "--debug", action="store_true",
        help="Show debug logs.")
    args = parser.parse_args()

    # Configure logger.
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.WARNING)

    # Find variant.
    VariantBoard = chess.variant.find_variant(args.variant)

    # Open engine.
    engine = chess.uci.popen_engine(args.engine)
    engine.uci()

    # Run each test line.
    score = 0.0
    count = 0

    for epd in itertools.chain(*args.epd):
        # Skip comments and empty lines.
        epd = epd.strip()
        if not epd or epd.startswith("#") or epd.startswith("%"):
            print(epd.rstrip())
            continue

        # Run the actual test.
        score += args.test_epd(engine, epd, VariantBoard, args.movetime)
        count += 1

    engine.quit()

    print("-------------------------------")
    print("%g / %d" % (score, count))
