# ================================================================
# LEGENDREQ-2003
# FIXED DATASET LOADER + ML DATA PREPARATION

#https://cricsheet.org/downloads/?utm_source=chatgpt.com
# ================================================================

import os
import zipfile
import json
from pathlib import Path
import pandas as pd

# ================================================================
# 1. UPLOAD ZIP
# ================================================================

try:
    from google.colab import files

    print("Please select:")
    print("icc_mens_cricket_world_cup_json.zip")

    uploaded = files.upload()

    if not uploaded:
        raise RuntimeError("No file was uploaded.")

    ZIP_PATH = next(iter(uploaded.keys()))

except ImportError:
    # For Jupyter/local environments
    ZIP_PATH = "icc_mens_cricket_world_cup_json.zip"

print("\nUsing ZIP:")
print(ZIP_PATH)

if not os.path.exists(ZIP_PATH):
    raise FileNotFoundError(
        f"ZIP file not found: {ZIP_PATH}"
    )

# ================================================================
# 2. OUTPUT DIRECTORY
# ================================================================

OUTPUT_DIR = Path(
    "/content/world_cup_2003_research_dataset"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

# ================================================================
# 3. READ ZIP
# ================================================================

matches = []
innings_rows = []
deliveries = []

skipped_files = []

with zipfile.ZipFile(
    ZIP_PATH,
    "r"
) as archive:

    json_names = [
        n for n in archive.namelist()
        if n.lower().endswith(".json")
        and not n.startswith("__MACOSX/")
    ]

    print(
        "\nJSON files in archive:",
        len(json_names)
    )

    for file_name in json_names:

        try:

            data = json.loads(
                archive.read(file_name)
            )

        except Exception as exc:

            skipped_files.append(
                (file_name, str(exc))
            )

            continue

        info = data.get(
            "info",
            {}
        )

        dates = info.get(
            "dates",
            []
        )

        # --------------------------------------------------------
        # YEAR FILTER
        # --------------------------------------------------------

        years = [
            str(d)[:4]
            for d in dates
        ]

        if "2003" not in years:
            continue

        # --------------------------------------------------------
        # EVENT FILTER
        # --------------------------------------------------------

        event = info.get(
            "event",
            {}
        )

        event_name = str(
            event.get(
                "name",
                ""
            )
        )

        combined_event = (
            event_name
            + " "
            + str(
                info.get(
                    "tournament",
                    ""
                )
            )
        ).lower()

        # We only want World Cup data.
        if "world cup" not in combined_event:
            continue

        # --------------------------------------------------------
        # MATCH INFORMATION
        # --------------------------------------------------------

        match_id = Path(
            file_name
        ).stem

        teams = info.get(
            "teams",
            []
        )

        toss = info.get(
            "toss",
            {}
        )

        outcome = info.get(
            "outcome",
            {}
        )

        winner = outcome.get(
            "winner",
            ""
        )

        if winner:
            result = (
                f"{winner} won"
            )
        elif outcome.get("result"):
            result = str(
                outcome.get("result")
            )
        elif outcome.get("method"):
            result = str(
                outcome.get("method")
            )
        else:
            result = "no winner recorded"

        matches.append({

            "match_id":
                match_id,

            "date":
                ";".join(
                    map(str, dates)
                ),

            "event":
                event_name,

            "match_number":
                event.get(
                    "match_number",
                    ""
                ),

            "group":
                event.get(
                    "group",
                    ""
                ),

            "team1":
                teams[0]
                if len(teams) > 0
                else "",

            "team2":
                teams[1]
                if len(teams) > 1
                else "",

            "venue":
                info.get(
                    "venue",
                    ""
                ),

            "city":
                (
                    ";".join(
                        info.get(
                            "city",
                            []
                        )
                    )
                    if isinstance(
                        info.get(
                            "city",
                            []
                        ),
                        list
                    )
                    else info.get(
                        "city",
                        ""
                    )
                ),

            "scheduled_overs":
                info.get(
                    "overs",
                    ""
                ),

            "balls_per_over":
                info.get(
                    "balls_per_over",
                    6
                ),

            "toss_winner":
                toss.get(
                    "winner",
                    ""
                ),

            "toss_decision":
                toss.get(
                    "decision",
                    ""
                ),

            "winner":
                winner,

            "result":
                result,

            "source_file":
                file_name
        })

        # ========================================================
        # INNINGS
        # ========================================================

        for innings_number, innings in enumerate(
            data.get(
                "innings",
                []
            ),
            start=1
        ):

            batting_team = innings.get(
                "team",
                ""
            )

            total_runs = 0
            total_wickets = 0
            legal_balls = 0
            delivery_count = 0

            for over_obj in innings.get(
                "overs",
                []
            ):

                over_number = over_obj.get(
                    "over",
                    0
                )

                for ball_number, ball in enumerate(
                    over_obj.get(
                        "deliveries",
                        []
                    ),
                    start=1
                ):

                    delivery_count += 1

                    runs = ball.get(
                        "runs",
                        {}
                    )

                    batter_runs = int(
                        runs.get(
                            "batter",
                            0
                        ) or 0
                    )

                    extras_runs = int(
                        runs.get(
                            "extras",
                            0
                        ) or 0
                    )

                    ball_runs = int(
                        runs.get(
                            "total",
                            batter_runs + extras_runs
                        ) or 0
                    )

                    extras = ball.get(
                        "extras",
                        {}
                    ) or {}

                    wickets = ball.get(
                        "wickets",
                        []
                    ) or []

                    wicket_flag = int(
                        len(wickets) > 0
                    )

                    wicket_kinds = ";".join(
                        str(
                            w.get(
                                "kind",
                                ""
                            )
                        )
                        for w in wickets
                    )

                    players_out = ";".join(
                        str(
                            w.get(
                                "player_out",
                                ""
                            )
                        )
                        for w in wickets
                    )

                    # ------------------------------------------------
                    # SCORE STATE
                    # ------------------------------------------------

                    total_runs += ball_runs
                    total_wickets += wicket_flag

                    # Wides and no-balls are not legal balls.
                    illegal_delivery = (
                        "wides" in extras
                        or
                        "noballs" in extras
                    )

                    if not illegal_delivery:
                        legal_balls += 1

                    # ------------------------------------------------
                    # DELIVERY RECORD
                    # ------------------------------------------------

                    deliveries.append({

                        "match_id":
                            match_id,

                        "date":
                            ";".join(
                                map(
                                    str,
                                    dates
                                )
                            ),

                        "event":
                            event_name,

                        "match_number":
                            event.get(
                                "match_number",
                                ""
                            ),

                        "stage_group":
                            event.get(
                                "group",
                                ""
                            ),

                        "innings":
                            innings_number,

                        "batting_team":
                            batting_team,

                        "over_index0":
                            over_number,

                        "ball_index_in_over":
                            ball_number,

                        "batter":
                            ball.get(
                                "batter",
                                ""
                            ),

                        "bowler":
                            ball.get(
                                "bowler",
                                ""
                            ),

                        "non_striker":
                            ball.get(
                                "non_striker",
                                ""
                            ),

                        "batter_runs":
                            batter_runs,

                        "extras_runs":
                            extras_runs,

                        "total_runs":
                            ball_runs,

                        "extras_json":
                            json.dumps(
                                extras,
                                sort_keys=True
                            ),

                        "is_wicket":
                            wicket_flag,

                        "wicket_kind":
                            wicket_kinds,

                        "player_out":
                            players_out,

                        "cumulative_runs":
                            total_runs,

                        "cumulative_wickets":
                            total_wickets,

                        "legal_balls_elapsed":
                            legal_balls
                    })

            innings_rows.append({

                "match_id":
                    match_id,

                "date":
                    ";".join(
                        map(
                            str,
                            dates
                        )
                    ),

                "innings":
                    innings_number,

                "batting_team":
                    batting_team,

                "delivery_records":
                    delivery_count,

                "legal_balls_recorded":
                    legal_balls,

                "runs_from_deliveries":
                    total_runs,

                "wickets_from_delivery_records":
                    total_wickets
            })


# ================================================================
# 4. DATAFRAMES
# ================================================================

matches_df = pd.DataFrame(
    matches
)

innings_df = pd.DataFrame(
    innings_rows
)

deliveries_df = pd.DataFrame(
    deliveries
)

if matches_df.empty:

    raise RuntimeError(
        "ZERO 2003 WORLD CUP MATCHES FOUND.\n\n"
        "This means the archive's event metadata "
        "uses a different tournament name."
    )

# ================================================================
# 5. SORT
# ================================================================

matches_df["date"] = pd.to_datetime(
    matches_df["date"].astype(str).str[:10],
    errors="coerce"
)

matches_df = (
    matches_df
    .sort_values(
        [
            "date",
            "match_id"
        ]
    )
    .reset_index(drop=True)
)

deliveries_df["date"] = pd.to_datetime(
    deliveries_df["date"].astype(str).str[:10],
    errors="coerce"
)

deliveries_df = (
    deliveries_df
    .sort_values(
        [
            "date",
            "match_id",
            "innings",
            "over_index0",
            "ball_index_in_over"
        ]
    )
    .reset_index(drop=True)
)

# ================================================================
# 6. SAVE
# ================================================================

matches_df.to_csv(
    OUTPUT_DIR / "matches_2003.csv",
    index=False
)

innings_df.to_csv(
    OUTPUT_DIR / "innings_2003.csv",
    index=False
)

deliveries_df.to_csv(
    OUTPUT_DIR / "deliveries_2003.csv",
    index=False
)

# ================================================================
# 7. REPORT
# ================================================================

print("\n" + "=" * 70)
print("LEGENDREQ-2003 DATASET")
print("=" * 70)

print(
    "Matches:",
    len(matches_df)
)

print(
    "Innings:",
    len(innings_df)
)

print(
    "Deliveries:",
    len(deliveries_df)
)

print(
    "Date range:",
    matches_df["date"].min(),
    "→",
    matches_df["date"].max()
)

print("\nMatches:")

print(
    matches_df[
        [
            "date",
            "team1",
            "team2",
            "winner"
        ]
    ].to_string(
        index=False
    )
)

print("\nSaved to:")
print(OUTPUT_DIR)

# ================================================================
# 8. NOW RUN THE ML CELL
# ================================================================

print("\nDataset ready.")
print(
    "You can now run the machine-learning cell."
)


###output

2003 CRICKET WORLD CUP DATASET BUILDER
======================================================================

Upload: icc_mens_cricket_world_cup_json.zip

Upload widget is only available when the cell has been executed in the current browser session. Please rerun this cell to enable.

Saving icc_mens_cricket_world_cup_json.zip to icc_mens_cricket_world_cup_json.zip

ZIP found: /content/icc_mens_cricket_world_cup_json.zip
Extracted to: /content/cricket_world_cup_json
Total JSON files found: 265

2003 World Cup JSON files detected: 49

======================================================================
DATASET CREATED SUCCESSFULLY
======================================================================

Matches: 49
Innings: 97
Deliveries: 25390

Files:
/content/world_cup_2003_research_dataset/matches_2003.csv
/content/world_cup_2003_research_dataset/innings_2003.csv
/content/world_cup_2003_research_dataset/deliveries_2003.csv

Matches by date:
 match_id       date        team1        team2       winner
        1 2003-02-09  West Indies South Africa  West Indies
        2 2003-02-10     Zimbabwe      Namibia     Zimbabwe
        3 2003-02-10    Sri Lanka  New Zealand    Sri Lanka
        4 2003-02-11    Australia     Pakistan    Australia
        5 2003-02-11       Canada   Bangladesh       Canada
        6 2003-02-12        Kenya South Africa South Africa
        7 2003-02-12        India  Netherlands        India
        8 2003-02-13  New Zealand  West Indies  New Zealand
        9 2003-02-15        India    Australia    Australia
       10 2003-02-15       Canada        Kenya        Kenya
       11 2003-02-16  Netherlands      England      England
       12 2003-02-16     Pakistan      Namibia     Pakistan
       13 2003-02-16 South Africa  New Zealand  New Zealand
       14 2003-02-18  West Indies   Bangladesh             
       15 2003-02-19        India     Zimbabwe        India
       16 2003-02-19       Canada    Sri Lanka    Sri Lanka
       17 2003-02-19      England      Namibia      England
       18 2003-02-22   Bangladesh South Africa South Africa
       19 2003-02-22      England     Pakistan      England
       20 2003-02-23       Canada  West Indies  West Indies
       21 2003-02-23        India      Namibia        India
       22 2003-02-24        Kenya    Sri Lanka        Kenya
       23 2003-02-24     Zimbabwe    Australia    Australia
       24 2003-02-25     Pakistan  Netherlands     Pakistan
       25 2003-02-26   Bangladesh  New Zealand  New Zealand
       26 2003-02-26        India      England        India
       27 2003-02-27    Australia      Namibia    Australia
       28 2003-02-27 South Africa       Canada South Africa
       29 2003-02-28     Zimbabwe  Netherlands     Zimbabwe
       30 2003-02-28    Sri Lanka  West Indies    Sri Lanka
       31 2003-03-01        Kenya   Bangladesh        Kenya
       32 2003-03-01     Pakistan        India        India
       33 2003-03-02      England    Australia    Australia
       34 2003-03-03       Canada  New Zealand  New Zealand
       35 2003-03-03  Netherlands      Namibia  Netherlands
       36 2003-03-03    Sri Lanka South Africa             
       37 2003-03-04     Pakistan     Zimbabwe             
       38 2003-03-07    Australia    Sri Lanka    Australia
       39 2003-03-07        Kenya        India        India
       40 2003-03-08     Zimbabwe  New Zealand  New Zealand
       41 2003-03-10        India    Sri Lanka        India
       42 2003-03-11    Australia  New Zealand    Australia
       43 2003-03-12     Zimbabwe        Kenya        Kenya
       44 2003-03-14  New Zealand        India        India
       45 2003-03-15    Sri Lanka     Zimbabwe    Sri Lanka
       46 2003-03-15        Kenya    Australia    Australia
       47 2003-03-18    Australia    Sri Lanka    Australia
       48 2003-03-20        India        Kenya        India
       49 2003-03-23    Australia        India    Australia

Delivery sample:

	match_id 	date 	innings 	batting_team 	batter 	bowler 	over 	ball_in_over 	legal_balls_elapsed 	total_runs 	batter_runs 	extras_runs 	is_wicket 	wicket_kind 	innings_cumulative_runs 	innings_cumulative_wickets
0 	1 	2003-02-09 	1 	West Indies 	CH Gayle 	SM Pollock 	0 	1 	1 	0 	0 	0 	0 		0 	0
1 	1 	2003-02-09 	1 	West Indies 	CH Gayle 	SM Pollock 	0 	2 	2 	0 	0 	0 	0 		0 	0
2 	1 	2003-02-09 	1 	West Indies 	CH Gayle 	SM Pollock 	0 	3 	3 	0 	0 	0 	0 		0 	0
3 	1 	2003-02-09 	1 	West Indies 	CH Gayle 	SM Pollock 	0 	4 	4 	0 	0 	0 	0 		0 	0
4 	1 	2003-02-09 	1 	West Indies 	CH Gayle 	SM Pollock 	0 	5 	5 	0 	0 	0 	0 		0 	0
5 	1 	2003-02-09 	1 	West Indies 	CH Gayle 	SM Pollock 	0 	6 	6 	0 	0 	0 	0 		0 	0
6 	1 	2003-02-09 	1 	West Indies 	WW Hinds 	M Ntini 	1 	1 	7 	0 	0 	0 	0 		0 	0
7 	1 	2003-02-09 	1 	West Indies 	WW Hinds 	M Ntini 	1 	2 	8 	0 	0 	0 	0 		0 	0
8 	1 	2003-02-09 	1 	West Indies 	WW Hinds 	M Ntini 	1 	3 	9 	0 	0 	0 	0 		0 	0
9 	1 	2003-02-09 	1 	West Indies 	WW Hinds 	M Ntini 	1 	4 	10 	0 	0 	0 	0 		0 	0


Target distribution:
0    13608
1     7473
2     1386
3      177
4     1749
5      301
6      696
Name: count, dtype: int64

Ready for the ML cell.

✓ deliveries_2003.csv exists
✓ Delivery rows: 25390
✓ You can now run the ML cell.

