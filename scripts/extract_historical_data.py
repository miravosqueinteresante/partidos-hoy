"""
FIFA World Cup Historical Technical Report Parser
Extracts structured match data from TXT reports (1970-2018).
"""

import re
import json
import os
from datetime import datetime

INPUT_DIR = r"C:\Users\pc\Desktop\Proyectos\Mundial\Reportes Historicos Mundiales"
OUTPUT_FILE = r"C:\Users\pc\Desktop\Proyectos\Predicciones Futbol\data\historical_wc_data.json"
SKIP_FILES = {"2022_Qatar_In_Numbers.txt"}

SOURCE_FILES = [
    f for f in sorted(os.listdir(INPUT_DIR))
    if f.endswith(".txt") and f not in SKIP_FILES
]


def read_file(filename):
    path = os.path.join(INPUT_DIR, filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().splitlines()
    except UnicodeDecodeError:
        with open(path, "r", encoding="latin-1", errors="replace") as f:
            return f.read().splitlines()


def parse_scorers(text):
    scorers = []
    if not text or text.strip() in ("-", "–", ""):
        return scorers
    text = text.replace("\n", " ").replace("\r", " ").strip()
    # Match patterns like: 1-0 12' GAZINSKY (8), 2-0 43' CHERYSHEV (6)
    # or: 0-1 89' GIMENEZ (2)
    parts = re.split(r',\s*(?=\d+-\d+)', text)
    for part in parts:
        part = part.strip()
        if not part:
            continue
        m = re.match(r'(\d+)-(\d+)\s+(\d+)’\+?(\d*)\s*(.+?)(?:\(|$)', part)
        if m:
            hs, aws, minute, extra, rest = m.group(1), m.group(2), int(m.group(3)), m.group(4), m.group(5).strip()
            team = "home" if int(hs) > int(aws) or (int(hs) == 1 and int(aws) != 1) else "away"
            player = rest.rstrip().rstrip(",")
            entry = {"player": player, "minute": minute, "team": team, "score": f"{hs}-{aws}"}
            if extra:
                entry["extra_time"] = f"+{extra}"
            if "own goal" in part.lower() or "og" in part.lower():
                entry["type"] = "own_goal"
            if "pen" in part.lower():
                entry["type"] = "penalty"
            scorers.append(entry)
        else:
            m2 = re.match(r'(\d+)-(\d+)\s+(\d+)’\s*(.+)', part)
            if m2:
                hs, aws, minute, rest = m2.groups()
                team = "home" if int(hs) > int(aws) or (int(hs) == 1 and int(aws) != 1) else "away"
                scorers.append({"player": rest.strip(), "minute": int(minute), "team": team, "score": f"{hs}-{aws}"})
    return scorers


def parse_2018(lines):
    """Parse 2018 report - scan for overview pairs then parse match detail blocks."""
    matches = []
    year = 2018
    n = len(lines)
    i = 0

    # Find MATCH INFORMATION section
    while i < n:
        if "MATCH INFORMATION" in lines[i].strip():
            break
        i += 1
    if i >= n:
        return []

    # FIRST PASS: collect all overview pairs and match positions
    overviews = []  # (line_num, ht, at, hs, aws, hth, hta)
    match_starts = []  # (line_num, match_number)

    current_group = None
    i = 0
    while i < n:
        line = lines[i].strip()
        gm = re.search(r'MATCH INFORMATION:\s*GROUP\s*([A-H])', line)
        if gm:
            current_group = gm.group(1)

        tm = re.match(r'^([A-Za-z\s]+)\s+v\.\s+([A-Za-z\s]+?)\s*$', line)
        if tm:
            ht = tm.group(1).strip()
            at = tm.group(2).strip()
            if len(ht) <= 30 and len(at) <= 30 and i + 1 < n:
                sl = lines[i+1].strip()
                sm = re.match(r'(\d+)-(\d+)\s*\((\d+)-(\d+)\)', sl)
                if sm:
                    overviews.append((i, ht, at, int(sm.group(1)), int(sm.group(2)), int(sm.group(3)), int(sm.group(4))))
                    i += 2
                    continue
                sm2 = re.match(r'(\d+)-(\d+)', sl)
                if sm2:
                    overviews.append((i, ht, at, int(sm2.group(1)), int(sm2.group(2)), None, None))
                    i += 2
                    continue

        mn_match = re.match(r'^(\d{1,2})\s*$', line)
        if mn_match and i + 1 < n:
            # Date may be on same line as time or on separate lines
            nxt = lines[i+1].strip()
            nd = re.match(r'(\d{2})\.(\d{2})\.(\d{4})\s+(\d{2}:\d{2})', nxt)
            if not nd:
                nd = re.match(r'(\d{2})\.(\d{2})\.(\d{4})\s*$', nxt)
            if nd:
                match_starts.append((i, int(mn_match.group(1)), current_group))
                i += 1
                continue
        i += 1

    # Match overviews to match numbers by proximity (find closest upcoming overview)
    for idx, (start_line, mn, group) in enumerate(match_starts):
        # Find overview closest to this match number (the one immediately before or at most 10 lines before)
        best_ov = None
        best_dist = 99999
        for ov_idx, ov in enumerate(overviews):
            ov_line = ov[0]
            dist = start_line - ov_line
            if 0 <= dist < best_dist and dist < 50:
                best_ov = ov_idx
                best_dist = dist

        ht, at, hs, aws, hth, hta = "", "", None, None, None, None
        if best_ov is not None:
            ov = overviews.pop(best_ov)
            ht, at, hs, aws, hth, hta = ov[1], ov[2], ov[3], ov[4], ov[5], ov[6]

        i = start_line
        date_line = lines[i+1].strip()
        nd = re.match(r'(\d{2})\.(\d{2})\.(\d{4})\s+(\d{2}:\d{2})', date_line)
        time_str = ""
        if nd:
            date_str = f"{nd.group(3)}-{nd.group(2)}-{nd.group(1)}"
            time_str = nd.group(4)
            rest_line = date_line[nd.end():].strip()
            venue = rest_line
            att_idx = i + 2 if rest_line else i + 3
        else:
            nd = re.match(r'(\d{2})\.(\d{2})\.(\d{4})\s*$', date_line)
            if nd:
                date_str = f"{nd.group(3)}-{nd.group(2)}-{nd.group(1)}"
                if i + 2 < n:
                    time_str = lines[i+2].strip()
                    venue = lines[i+3].strip() if i+3 < n else ""
                    att_idx = i + 4
                else:
                    venue = ""
                    att_idx = i + 2
            else:
                date_str = ""
                venue = ""
                att_idx = i + 2
        attendance = None
        if att_idx < n:
            a = lines[att_idx].strip().replace(",", "")
            if a.isdigit():
                attendance = int(a)
            else:
                att_idx += 1
                if att_idx < n:
                    a = lines[att_idx].strip().replace(",", "")
                    if a.isdigit():
                        attendance = int(a)

        home_code, away_code = "", ""
        home_lineup, away_lineup = [], []
        home_subs, away_subs = [], []
        home_cautions, away_cautions = [], []
        expulsions = []
        scorers = []
        referee = ""

        j = att_idx + 1 if attendance else i + 5
        safety = 0
        while j < n and safety < 200:
            safety += 1
            l = lines[j].strip()
            if not l:
                j += 1
                continue

            # Next match?
            nnm = re.match(r'^(\d{1,2})\s*$', l)
            if nnm and j + 1 < n:
                nd2 = re.match(r'(\d{2})\.(\d{2})\.(\d{4})', lines[j+1].strip())
                if nd2 and int(nnm.group(1)) != mn:
                    break

            if l.startswith("Data provided") or l.startswith("MATCH INFORMATION:") or l.startswith("See match highlights:"):
                break
            if re.match(r'^\d{3,}\s*$', l):
                j += 1
                continue
            if l.startswith("2018 FIFA World Cup"):
                j += 1
                continue

            if l.startswith("Scorers:"):
                st = ""
                j += 1
                while j < n:
                    nl = lines[j].strip()
                    if not nl or nl.startswith(("Referee:", "Substitutions:", "Cautions:", "Expulsions:", "See match", "Data")):
                        break
                    st += " " + nl
                    j += 1
                scorers = parse_scorers(st)
                continue

            if l.startswith("Referee:"):
                referee = l[8:].strip()
                j += 1
                continue

            if l.startswith("Substitutions:"):
                j += 1
                while j < n:
                    nl = lines[j].strip()
                    if not nl or nl.startswith(("Cautions:", "Expulsions:", "See match", "Data")):
                        break
                    if re.match(r'^\d{1,2}\s*$', nl) and j+1 < n and re.match(r'\d{2}\.\d{2}\.\d{4}', lines[j+1].strip()):
                        break
                    sm = re.match(r"(?:(\w{3,4}):?\s+)?(\d+)'\+?(\d*)\s*out\s+(.+?),\s*in\s+(.+)", nl)
                    if sm:
                        tc = (sm.group(1) or "").upper()
                        entry = {"out": sm.group(4).strip(), "in": sm.group(5).strip(), "minute": int(sm.group(2))}
                        if tc in ("", home_code):
                            home_subs.append(entry)
                        else:
                            away_subs.append(entry)
                    j += 1
                continue

            if l.startswith("Cautions:"):
                j += 1
                while j < n:
                    nl = lines[j].strip()
                    if not nl or nl.startswith(("Expulsions:", "See match", "Data")):
                        break
                    for c in re.findall(r"(\d+)'\+?(\d*)\s+([A-Z][A-Z\s]+?)(?:\s*\(\d+\))?", nl):
                        entry = {"player": c[2].strip(), "minute": int(c[0])}
                        if c[1]: entry["extra_time"] = f"+{c[1]}"
                        away_cautions.append(entry)
                    j += 1
                continue

            if l.startswith("Expulsions:"):
                j += 1
                while j < n:
                    nl = lines[j].strip()
                    if not nl or nl.startswith(("See match", "Data")):
                        break
                    if nl not in ("-", "–"):
                        expulsions.append(nl)
                        j += 1
                    else:
                        j += 1
                        break
                continue

            tc = re.match(r'^([A-Z]{3,4}):\s*(.*)', l)
            if tc:
                code = tc.group(1).upper()
                rest = tc.group(2).strip()
                if not home_code:
                    home_code = code
                    home_lineup = [rest] if rest else []
                elif code == home_code:
                    if rest: home_lineup.append(rest)
                elif not away_code:
                    away_code = code
                    away_lineup = [rest] if rest else []
                elif code == away_code:
                    if rest: away_lineup.append(rest)
                j += 1
                continue

            j += 1

        if mn >= 49:
            stg_map = {49: "round_of_16", 50: "round_of_16", 51: "round_of_16", 52: "round_of_16",
                       53: "round_of_16", 54: "round_of_16", 55: "round_of_16", 56: "round_of_16",
                       57: "quarter_final", 58: "quarter_final", 59: "quarter_final", 60: "quarter_final",
                       61: "semi_final", 62: "semi_final", 63: "third_place", 64: "final"}
            stg = stg_map.get(mn, "knockout")
            matches.append({
                "year": year, "stage": stg, "group": group if stg == "group" else None,
                "round": stg, "match_number": mn,
                "date": date_str, "venue": venue, "attendance": attendance,
                "home_team": ht, "away_team": at,
                "home_score": hs, "away_score": aws,
                "half_time_home": hth, "half_time_away": hta,
                "scorers": scorers, "referee": referee,
                "home_lineup": home_lineup, "away_lineup": away_lineup,
                "home_substitutions": home_subs, "away_substitutions": away_subs,
                "home_cautions": home_cautions, "away_cautions": away_cautions,
                "expulsions": expulsions
            })
        else:
            matches.append({
                "year": year, "stage": "group", "group": group,
                "round": "group_stage", "match_number": mn,
                "date": date_str, "venue": venue, "attendance": attendance,
                "home_team": ht, "away_team": at,
                "home_score": hs, "away_score": aws,
                "half_time_home": hth, "half_time_away": hta,
                "scorers": scorers, "referee": referee,
                "home_lineup": home_lineup, "away_lineup": away_lineup,
                "home_substitutions": home_subs, "away_substitutions": away_subs,
                "home_cautions": home_cautions, "away_cautions": away_cautions,
                "expulsions": expulsions
            })

    print(f"  2018 Parser: found {len(matches)} matches")
    return matches


def parse_2014_2010(lines, year):
    """Parse 2014 and 2010 reports."""
    matches = []
    in_telegrams = False
    current_group = None
    n = len(lines)
    i = 0

    # Find the Match telegrams section
    while i < n:
        if lines[i].strip() == "Match telegrams":
            in_telegrams = True
            i += 1
            break
        i += 1

    if not in_telegrams:
        return []

    # Skip group header
    while i < n:
        line = lines[i].strip()
        gm = re.match(r'[Gg][Rr][Oo][Uu][Pp]\s+([A-H])', line)
        if gm:
            current_group = gm.group(1)
            i += 1
            break
        if line:
            i += 1
        else:
            i += 1

    # Now parse match blocks
    while i < n:
        line = lines[i].strip()

        # Update group
        gm = re.match(r'[Gg][Rr][Oo][Uu][Pp]\s+([A-H])', line)
        if gm:
            current_group = gm.group(1)
            i += 1
            continue

        if not line or line.startswith("Match telegrams") or re.match(r'^\d+\s*$', line):
            i += 1
            continue

        # Detect start of match: standalone team v team line
        # The format is: after lineups + data, the match header line appears
        # "Team v. Team" then score on next line
        tm = re.match(r'^([A-Za-zÀ-ÿ\s]+)\s+v\.\s+([A-Za-zÀ-ÿ\s]+?)\s*$', line)
        if not tm:
            i += 1
            continue

        ht = tm.group(1).strip()
        at = tm.group(2).strip()
        if len(ht) > 30 or len(at) > 30:
            i += 1
            continue

        # Score line
        if i + 1 >= n:
            i += 1
            continue
        sl = lines[i+1].strip()
        sm = re.match(r'(\d+)-(\d+)(?:\s*\((\d+)-(\d+)\))?', sl)
        if not sm:
            i += 1
            continue

        home_score = int(sm.group(1))
        away_score = int(sm.group(2))
        ht_home = int(sm.group(3)) if sm.group(3) else None
        ht_away = int(sm.group(4)) if sm.group(4) else None

        # Match number line
        mn = None
        if i + 2 < n:
            mnl = lines[i+2].strip()
            mnm = re.match(r'^(\d+)\s*$', mnl)
            if mnm:
                mn = int(mnm.group(1))

        # Date/venue line
        date_str = ""
        venue = ""
        attendance = None
        base = i + 3
        if base < n:
            dl = lines[base].strip()
            dm = re.match(r'(\d{2})\.(\d{2})\.(\d{4})\s+(\d{2}:\d{2})\s*(.*)', dl)
            if dm:
                date_str = f"{dm.group(3)}-{dm.group(2)}-{dm.group(1)}"
                venue = dm.group(5).strip()
                base += 1
            else:
                dm2 = re.match(r'(\d{2})\.(\d{2})\.(\d{4})\s*$', dl)
                if dm2:
                    date_str = f"{dm2.group(3)}-{dm2.group(2)}-{dm2.group(1)}"
                    base += 1
                    if base < n:
                        tl = lines[base].strip()
                        if re.match(r'\d{2}:\d{2}', tl):
                            base += 1
                    if base < n:
                        vl = lines[base].strip()
                        if vl and not re.match(r'^[\d,]+$', vl.replace(",", "")):
                            venue = vl
                            base += 1

            # Attendance
            if base < n:
                al = lines[base].strip().replace(",", "")
                if al.isdigit():
                    attendance = int(al)
                    base += 1

        # Now parse the match details (lineups etc.) that come BEFORE the team names
        # In 2014, the match data is BACKWARDS: lineups come first, then team names
        # But actually in 2014, the first match has format:
        # Match telegrams
        # GROUP A
        # 2  (match number for Mexico v Cameroon - 2nd group match)
        # 13.06.2014
        # 13:00
        # NATAL
        # 39,216
        # MEX:
        # <players>
        # CMR:
        # <players>
        # Scorers:
        # Referee:
        # Substitutions:
        # Cautions:
        # Expulsions:
        # Mexico v. Cameroon (team names)
        # 1-0 (0-0) (score)
        # 1 (match number for Brazil v Croatia - 1st match)
        # 12.06.2014
        # 17:00
        # SAO PAULO
        # 62,103
        # BRA:
        # <players>
        # CRO:
        # <players>
        # ...

        # So the team names appear AFTER the match details,
        # and the match number for the NEXT match appears on the score line + 1

        # I need to look BACKWARD from the team names to find the match data.
        # Actually, let me try a different approach: look for the match number,
        # then read forward for date/venue/attendance/lineups/etc,
        # then the team names appear after all that.

        # Reset and go back to the match number to read forward
        # Actually, let me re-start from where we had the match number

        # OK, let me fix this. The structure for 2014 is:
        # <match number>
        # <date>
        # <time> (or on same line as date)
        # <venue>
        # <attendance>
        # <team_code>: <players>
        # ... lineups ...
        # Scorers:
        # Referee:
        # Substitutions:
        # Cautions:
        # Expulsions:
        # <home_team> v. <away_team>  <-- this is where we are
        # <score>
        # <next_match_number>
        # ...

        # So from here (team names), I need to go BACKWARD to find
        # expulsions/cautions/subs/referee/scorers/lineups/attendance/venue/date/number

        # Let me search backward from i-1
        home_lineup, away_lineup = [], []
        home_subs, away_subs = [], []
        home_cautions, away_cautions = [], []
        expulsions = []
        scorers = []
        referee = ""

        j = i - 1
        state = "searching"
        while j >= 0:
            l = lines[j].strip()
            if not l:
                j -= 1
                continue

            if state == "searching":
                if l.startswith("Expulsions:"):
                    state = "expulsions"
                    j -= 1
                    continue
                if l.startswith("Cautions:"):
                    state = "cautions"
                    j -= 1
                    continue
                if l.startswith("Substitutions:"):
                    state = "subs"
                    j -= 1
                    continue
                if l.startswith("Referee:"):
                    referee = l[len("Referee:"):].strip()
                    state = "referee"
                    j -= 1
                    continue
                if l.startswith("Scorers:"):
                    state = "scorers"
                    j -= 1
                    continue
            elif state == "expulsions":
                if l not in ("-", "–"):
                    expulsions.append(l)
                else:
                    state = "searching"
                j -= 1
                continue
            elif state == "cautions":
                if re.match(r'[A-Z]{3,4}:?\s', l) or re.match(r'\d+', l):
                    for c in re.findall(r"(\d+)'\+?(\d*)\s+([A-Z][A-Z\s]+?)(?:\s*\(\d+\))?", l):
                        entry = {"player": c[2].strip(), "minute": int(c[0])}
                        if c[1]:
                            entry["extra_time"] = f"+{c[1]}"
                        away_cautions.append(entry)
                elif l.startswith("Cautions:"):
                    pass
                else:
                    state = "searching"
                    j += 1
                j -= 1
                continue
            elif state == "subs":
                sub_m = re.match(r"(?:(\w{3,4}):?\s+)?(\d+)'\+?(\d*)\s*out\s+(.+?),\s*in\s+(.+)", l)
                if sub_m:
                    tc = sub_m.group(1) or ""
                    minute = int(sub_m.group(2))
                    out_p = sub_m.group(4).strip()
                    in_p = sub_m.group(5).strip()
                    entry = {"out": out_p, "in": in_p, "minute": minute}
                    if tc.upper() in ("", "BRA", "MEX", "CMR", "CRO"):
                        away_subs.append(entry)
                    else:
                        home_subs.append(entry)
                elif re.match(r'[A-Z]{3,4}:', l):
                    pass
                else:
                    state = "searching"
                j -= 1
                continue
            elif state == "scorers":
                if not l.startswith("Scorers:") and l.strip():
                    stext = l
                    while j-1 >= 0:
                        nl = lines[j-1].strip()
                        if nl.startswith("Scorers:") or re.match(r'^[A-Z]{3}:', nl):
                            break
                        stext = nl + " " + stext
                        j -= 1
                    scorers = parse_scorers(stext)
                    state = "searching"
                j -= 1
                continue

            # Check if we've reached the lineup section
            tc_match = re.match(r'^([A-Z]{3,4}):\s*(.*)', l)
            if tc_match:
                code = tc_match.group(1)
                rest = tc_match.group(2)
                players = [rest] if rest else []
                j2 = j - 1
                while j2 >= 0:
                    nl = lines[j2].strip()
                    if not nl or re.match(r'^[A-Z]{3,4}:', nl):
                        break
                    if re.match(r'^\d+\s+[A-Z]', nl):
                        players.insert(0, nl)
                    j2 -= 1
                if away_lineup:
                    home_lineup = list(reversed(players))
                else:
                    away_lineup = list(reversed(players))
                j = j2

            # Check for attendance/venue/date/number
            al = l.replace(",", "")
            if al.isdigit() and len(al) >= 4 and attendance is None:
                attendance = int(al)
                j -= 1
                continue
            if venue == "" and l and not re.match(r'\d{2}\.\d{2}\.\d{4}', l) and not re.match(r'\d{2}:\d{2}', l) and l.isupper():
                venue = l
                j -= 1
                continue
            if re.match(r'^\d+\s*$', l) and len(l.strip()) <= 2:
                if mn is None:
                    mn = int(l.strip())
                j -= 1
                continue
            if re.match(r'\d{2}\.\d{2}\.\d{4}', l) and not date_str:
                dm = re.match(r'(\d{2})\.(\d{2})\.(\d{4})', l)
                if dm:
                    date_str = f"{dm.group(3)}-{dm.group(2)}-{dm.group(1)}"
                j -= 1
                continue

            j -= 1

        # Determine round
        round_name = "group_stage"
        stage = "group"
        if year == 2014:
            if mn and mn >= 49 and mn <= 56:
                round_name = "round_of_16"; stage = "round_of_16"
            elif mn and mn >= 57 and mn <= 60:
                round_name = "quarter_final"; stage = "quarter_final"
            elif mn and mn >= 61 and mn <= 62:
                round_name = "semi_final"; stage = "semi_final"
            elif mn == 63:
                round_name = "third_place"; stage = "third_place"
            elif mn == 64:
                round_name = "final"; stage = "final"
        elif year == 2010:
            if mn and mn >= 49 and mn <= 56:
                round_name = "round_of_16"; stage = "round_of_16"
            elif mn and mn >= 57 and mn <= 60:
                round_name = "quarter_final"; stage = "quarter_final"
            elif mn and mn >= 61 and mn <= 62:
                round_name = "semi_final"; stage = "semi_final"
            elif mn == 63:
                round_name = "third_place"; stage = "third_place"
            elif mn == 64:
                round_name = "final"; stage = "final"

        match = {
            "year": year, "stage": stage, "group": current_group,
            "round": round_name, "match_number": mn,
            "date": date_str, "venue": venue, "attendance": attendance,
            "home_team": ht, "away_team": at,
            "home_score": home_score, "away_score": away_score,
            "half_time_home": ht_home, "half_time_away": ht_away,
            "scorers": scorers, "referee": referee,
            "home_lineup": home_lineup, "away_lineup": away_lineup,
            "home_substitutions": home_subs, "away_substitutions": away_subs,
            "home_cautions": home_cautions, "away_cautions": away_cautions,
            "expulsions": expulsions
        }
        matches.append(match)
        i += 2

    # For 2010/2014, keep only final tournament matches (1-64)
    ft_matches = [m for m in matches if m.get("match_number") and 1 <= m["match_number"] <= 64]
    print(f"  {year} Parser: found {len(matches)} raw, {len(ft_matches)} final tournament")
    return ft_matches


def parse_2002(lines):
    """Parse 2002 report."""
    matches = []
    year = 2002
    n = len(lines)
    i = 0

    while i < n:
        line = lines[i].strip()

        if "Statistics" in line and "Match" in line:
            break
        i += 1

    if i >= n:
        return []

    # Format:
    # France - Senegal
    # 0-1 (0-1)
    # 1           31.05.2002     20:30     Seoul                                                  62,561
    # FRA:      3 LIZARAZU...
    # SEN:      1 SYLVA....
    # Scorers:
    # Referee:
    # Substitutions:
    # Cautions:
    # Expulsions:

    while i < n:
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        tm = re.match(r'^([A-Za-zÀ-ÿ\s]+)\s*[–-]\s*([A-Za-zÀ-ÿ\s]+?)\s*$', line)
        if tm:
            ht = tm.group(1).strip()
            at = tm.group(2).strip()
            if len(ht) > 30 or len(at) > 30:
                i += 1
                continue

            if i + 1 >= n:
                i += 1
                continue
            sl = lines[i+1].strip()
            sm = re.match(r'(\d+)-(\d+)(?:\s*\((\d+)-(\d+)\))?', sl)
            if not sm:
                i += 1
                continue

            home_score = int(sm.group(1))
            away_score = int(sm.group(2))
            ht_home = int(sm.group(3)) if sm.group(3) else None
            ht_away = int(sm.group(4)) if sm.group(4) else None

            # Info line
            info_line = lines[i+2].strip() if i+2 < n else ""
            im = re.match(r'(\d+)\s+(\d{2})\.(\d{2})\.(\d{4})\s+(\d{2}:\d{2})\s+(.*?)\s+([\d,]+)\s*$', info_line)
            mn = None
            date_str = ""
            venue = ""
            attendance = None
            if im:
                mn = int(im.group(1))
                date_str = f"{im.group(4)}-{im.group(3)}-{im.group(2)}"
                venue = im.group(6).strip()
                attendance = int(im.group(7).replace(",", ""))
            else:
                im2 = re.match(r'(\d+)\s+(\d{2})\.(\d{2})\.(\d{4})\s+(\d{2}:\d{2})\s+(.*)', info_line)
                if im2:
                    mn = int(im2.group(1))
                    date_str = f"{im2.group(4)}-{im2.group(3)}-{im2.group(2)}"
                    venue = im2.group(6).strip()

            home_lineup, away_lineup = [], []
            home_subs, away_subs = [], []
            home_cautions, away_cautions = [], []
            expulsions = []
            scorers = []
            referee = ""
            home_code = ""
            away_code = ""

            # Parse rest of match block
            j = i + 3
            while j < n:
                l = lines[j].strip()
                if not l:
                    j += 1
                    continue

                # Check for next match
                if re.match(r'^[A-Za-zÀ-ÿ\s]+[–-][A-Za-zÀ-ÿ\s]+$', l):
                    if j > i + 4:
                        break

                tc = re.match(r'^([A-Z]{3,4}):\s*(.*)', l)
                if tc:
                    code = tc.group(1)
                    rest = tc.group(2)
                    players = [rest] if rest else []
                    if not home_code:
                        home_code = code
                        home_lineup = players
                    elif code == home_code:
                        home_lineup.extend([rest]) if rest else None
                    elif not away_code:
                        away_code = code
                        away_lineup = players
                    else:
                        away_lineup.extend([rest]) if rest else None
                    j += 1
                    continue

                # Lineup continuation lines
                if re.match(r'^\d+\s+[A-Z]', l):
                    if not re.match(r'^\d+\s+[A-Z]', lines[min(j+1, n-1)].strip()):
                        pass
                    j += 1
                    continue

                if l.startswith("Scorers:"):
                    scorer_text = ""
                    j += 1
                    while j < n:
                        nl = lines[j].strip()
                        if not nl or nl.startswith("Referee:") or nl.startswith("Substitutions:") or nl.startswith("Cautions:") or nl.startswith("Expulsions:"):
                            break
                        if re.match(r'^[A-Z]{3}:', nl):
                            break
                        scorer_text += " " + nl
                        j += 1
                    scorers = parse_scorers(scorer_text)
                    continue

                if l.startswith("Referee:"):
                    referee = l[len("Referee:"):].strip()
                    j += 1
                    continue

                if l.startswith("Substitutions:"):
                    j += 1
                    current_sub = None
                    while j < n:
                        nl = lines[j].strip()
                        if not nl or nl.startswith("Cautions:") or nl.startswith("Expulsions:"):
                            break
                        sub_m = re.match(r"(?:(\d+)'\+?(\d*)\s+)?(\w{3,4}:)?\s*out\s+(.+?),\s*in\s+(.+)", nl)
                        if sub_m:
                            minute = int(sub_m.group(1)) if sub_m.group(1) else 0
                            out_p = sub_m.group(4).strip()
                            in_p = sub_m.group(5).strip()
                            entry = {"out": out_p, "in": in_p, "minute": minute}
                            if current_sub == home_code:
                                home_subs.append(entry)
                            else:
                                away_subs.append(entry)
                        elif re.match(r'[A-Z]{3}:', nl):
                            current_sub = nl.split(":")[0].strip()
                        j += 1
                    continue

                if l.startswith("Cautions:"):
                    j += 1
                    while j < n:
                        nl = lines[j].strip()
                        if not nl or nl.startswith("Expulsions:") or nl.startswith("Substitutions:"):
                            break
                        for c in re.findall(r"(\d+)'\+?(\d*)\s+([A-Z][A-Z\s]+?)(?:\s*\(\d+\))?", nl):
                            entry = {"player": c[2].strip(), "minute": int(c[0])}
                            if c[1]: entry["extra_time"] = f"+{c[1]}"
                            away_cautions.append(entry)
                        j += 1
                    continue

                if l.startswith("Expulsions:"):
                    j += 1
                    while j < n:
                        nl = lines[j].strip()
                        if not nl or nl in ("-", "–"):
                            break
                        expulsions.append(nl)
                        j += 1
                    break

                j += 1

            round_name = "group_stage"
            stage = "group"

            match = {
                "year": year, "stage": stage, "group": None,
                "round": round_name, "match_number": mn,
                "date": date_str, "venue": venue, "attendance": attendance,
                "home_team": ht, "away_team": at,
                "home_score": home_score, "away_score": away_score,
                "half_time_home": ht_home, "half_time_away": ht_away,
                "scorers": scorers, "referee": referee,
                "home_lineup": home_lineup, "away_lineup": away_lineup,
                "home_substitutions": home_subs, "away_substitutions": away_subs,
                "home_cautions": home_cautions, "away_cautions": away_cautions,
                "expulsions": expulsions
            }
            matches.append(match)
            i = j
            continue

        i += 1

    print(f"  2002 Parser: found {len(matches)} matches")
    return matches


def parse_1974(lines):
    """Parse 1974 report."""
    matches = []
    n = len(lines)
    i = 0

    while i < n:
        if "Statistical details of the Matches" in lines[i]:
            break
        i += 1

    if i >= n:
        return []

    # Skip the key/legend section and team abbreviations
    while i < n:
        line = lines[i].strip()
        if re.match(r'1St Final Round', line):
            break
        i += 1

    current_group = None

    while i < n:
        line = lines[i].strip()

        if not line:
            i += 1
            continue

        # Group header (check BEFORE skip patterns since group line may contain / Groupe etc.)
        gm = re.match(r'Group\s+(\d)\s*/', line)
        if gm:
            current_group = "Group " + gm.group(1)
            i += 1
            continue

        # Skip multi-language header lines that are NOT group headers
        if "/ Groupe" in line or "/ Grupo" in line or "/ Gruppe" in line:
            i += 1
            continue

        # Match number: "01", "02", etc.
        mn_match = re.match(r'^(\d{1,2})\s*$', line)
        if mn_match and i + 4 < n:
            mn = int(mn_match.group(1))
            date_line = lines[i+1].strip()
            time_line = ""
            # Format: date on line i+1, time on i+2 or combined
            dm = re.match(r'(\d{2})\.(\d{2})\.(\d{2})', date_line)
            if not dm:
                i += 1
                continue

            date_str = f"19{dm.group(3)}-{dm.group(2)}-{dm.group(1)}"
            venue = ""
            if i+2 < n:
                venue = lines[i+2].strip()
            team_line = lines[i+3].strip() if i+3 < n else ""
            score_line = lines[i+4].strip() if i+4 < n else ""

            # Team names: "GER -CHI" or "GDR - AUS"
            tm = re.match(r'(\w+)\s*[–-]\s*([A-Z]+)', team_line)
            if tm:
                home_team = tm.group(1).strip()
                away_team = tm.group(2).strip()
            else:
                tm2 = re.match(r'(\w+)\s*[–-]?\s*([A-Z]+)', team_line)
                if tm2:
                    home_team = tm2.group(1).strip()
                    away_team = tm2.group(2).strip()
                else:
                    i += 1
                    continue

            # Score: "1:0 (1:0" or "2:0 (0:0)"
            scm = re.match(r'(\d+)\s*:\s*(\d+)\s*\((\d+)\s*:\s*(\d+)', score_line)
            if scm:
                home_score = int(scm.group(1))
                away_score = int(scm.group(2))
                ht_home = int(scm.group(3))
                ht_away = int(scm.group(4))
            else:
                i += 1
                continue

            attendance = None
            # Find attendance in the block (look for "d)" section)
            j = i + 5
            while j < n:
                l = lines[j].strip()
                if l == "d)" and j+1 < n:
                    att_str = lines[j+1].strip().replace(" ", "")
                    if att_str.isdigit():
                        attendance = int(att_str)
                    break
                if re.match(r'^\d{1,2}\s*$', l) and j > i + 5:
                    break
                if l.startswith("Group") or l.startswith("1St Final Round"):
                    break
                j += 1

            tmap = {
                "GER": "Germany FR", "CHI": "Chile", "GDR": "German DR",
                "AUS": "Australia", "HOL": "Netherlands", "URU": "Uruguay",
                "SWE": "Sweden", "BUL": "Bulgaria", "HAI": "Haiti",
                "ITA": "Italy", "POL": "Poland", "ARG": "Argentina",
                "SCO": "Scotland", "ZAI": "Zaire", "YUG": "Yugoslavia",
                "BRA": "Brazil"
            }

            match = {
                "year": 1974, "stage": "group", "group": current_group,
                "round": "first_final_round", "match_number": mn,
                "date": date_str, "venue": venue, "attendance": attendance,
                "home_team": tmap.get(home_team, home_team),
                "away_team": tmap.get(away_team, away_team),
                "home_score": home_score, "away_score": away_score,
                "half_time_home": ht_home, "half_time_away": ht_away,
                "scorers": [], "referee": "",
                "home_lineup": [], "away_lineup": [],
                "home_substitutions": [], "away_substitutions": [],
                "home_cautions": [], "away_cautions": [], "expulsions": []
            }
            matches.append(match)

        i += 1

    print(f"  1974 Parser: found {len(matches)} matches")
    return matches


def parse_2006(lines):
    """Parse 2006 report - extract final tournament matches from team data sections."""
    matches = []
    n = len(lines)

    # Look for date + Team v Team + score patterns in the file
    # Format: "dd.mm.yy Team v. Team" then score on next line
    for i in range(n - 1):
        line = lines[i].strip()
        dm = re.match(r'(\d{2})\.(\d{2})\.(\d{2})\s+(.+)\s+v\.\s+(.+)', line)
        if not dm:
            continue
        date_str = ""
        if dm.group(3) == "06":
            date_str = f"2006-{dm.group(2)}-{dm.group(1)}"
        ht = dm.group(4).strip()
        at = dm.group(5).strip()
        if len(ht) > 35 or len(at) > 35:
            continue

        sl = lines[i+1].strip()
        sm = re.match(r'(\d+)-(\d+)(?:\s*\((\d+)-(\d+)\))?', sl)
        if not sm:
            # Check for extra time results: "0-0 a.e.t., 0-3 PSO"
            sm = re.match(r'(\d+)-(\d+)\s+a\.e\.t\.', sl)
            if not sm:
                continue
            hs = int(sm.group(1))
            aws = int(sm.group(2))
        else:
            hs = int(sm.group(1))
            aws = int(sm.group(2))

        hth = int(sm.group(3)) if sm.lastindex and sm.group(3) else None
        hta = int(sm.group(4)) if sm.lastindex and sm.group(4) else None

        matches.append({
            "year": 2006, "stage": "unknown", "group": None,
            "round": "unknown", "match_number": None,
            "date": date_str, "venue": "", "attendance": None,
            "home_team": ht, "away_team": at,
            "home_score": hs, "away_score": aws,
            "half_time_home": hth, "half_time_away": hta,
            "scorers": [], "referee": "",
            "home_lineup": [], "away_lineup": [],
            "home_substitutions": [], "away_substitutions": [],
            "home_cautions": [], "away_cautions": [], "expulsions": []
        })

    # Filter to only final tournament matches (played in June-July 2006)
    matches = deduplicate(matches)
    final_matches = [m for m in matches if m["date"] and m["date"].startswith("2006-")]
    print(f"  2006 Parser: found {len(matches)} raw, {len(final_matches)} final tournament")
    return final_matches[:64]  # Keep at most 64 final tournament matches


def parse_1970_1998(lines, year):
    """Generic parser for older reports - extract team vs team + score patterns."""
    matches = set()
    n = len(lines)

    for i in range(n - 1):
        line = lines[i].strip()
        if not line:
            continue

        # Try: Team v. Team score (halftime)
        m = re.match(r'^([A-Za-zÀ-ÿ\s]+)\s+v\.\s+([A-Za-zÀ-ÿ\s]+?)\s+(\d+)-(\d+)\s*(?:\((\d+)-(\d+)\))?', line)
        if not m:
            # Try: date Team v. Team (with score on next line)
            m = re.match(r'(\d{1,2}\.\d{1,2}\.\d{2,4})?\s*([A-Za-zÀ-ÿ\s]+)\s+v\.\s+([A-Za-zÀ-ÿ\s]+?)\s*$', line)
            if m:
                date_part = m.group(1) or ""
                ht = m.group(2).strip()
                at = m.group(3).strip()
                if len(ht) > 30 or len(at) > 30:
                    continue
                sl = lines[i+1].strip()
                sm = re.match(r'(\d+)-(\d+)\s*(?:\((\d+)-(\d+)\))?', sl)
                if sm:
                    date_str = ""
                    if date_part:
                        parts = re.split(r'[.\/]', date_part)
                        if len(parts) == 3:
                            yr = parts[2] if len(parts[2]) == 4 else f"19{parts[2]}"
                            date_str = f"{yr}-{int(parts[1]):02d}-{int(parts[0]):02d}"
                    matches.add((ht, at, int(sm.group(1)), int(sm.group(2)), date_str))
            continue

        ht = m.group(1).strip()
        at = m.group(2).strip()
        hs = int(m.group(3))
        aws = int(m.group(4))
        if len(ht) > 30 or len(at) > 30:
            continue
        matches.add((ht, at, hs, aws, ""))

    result = []
    for (ht, at, hs, aws, ds) in matches:
        result.append({
            "year": year, "stage": "unknown", "group": None,
            "round": "unknown", "match_number": None,
            "date": ds, "venue": "", "attendance": None,
            "home_team": ht, "away_team": at,
            "home_score": hs, "away_score": aws,
            "half_time_home": None, "half_time_away": None,
            "scorers": [], "referee": "",
            "home_lineup": [], "away_lineup": [],
            "home_substitutions": [], "away_substitutions": [],
            "home_cautions": [], "away_cautions": [], "expulsions": []
        })

    print(f"  {year} Parser: found {len(result)} matches")
    return result


def deduplicate(matches):
    seen = set()
    unique = []
    for m in matches:
        key = (m["year"], m["home_team"], m["away_team"], m["home_score"], m["away_score"], m.get("match_number"), m.get("date", ""))
        if key not in seen:
            seen.add(key)
            unique.append(m)
    return unique


def parse_file(filename):
    lines = read_file(filename)
    ym = re.search(r'(\d{4})', filename)
    year = int(ym.group(1)) if ym else 0

    print(f"Processing: {filename} (year={year})", end="")

    if year >= 2018:
        matches = parse_2018(lines)
    elif year == 2014:
        matches = parse_2014_2010(lines, 2014)
    elif year == 2010:
        matches = parse_2014_2010(lines, 2010)
    elif year == 2002:
        matches = parse_2002(lines)
    elif year == 2006:
        matches = parse_2006(lines)
    elif year == 1974:
        matches = parse_1974(lines)
    elif year in (1970, 1978, 1982, 1986, 1990, 1998):
        matches = parse_1970_1998(lines, year)
    else:
        matches = parse_1970_1998(lines, year)

    print(f" -> {len(matches)} matches")
    return matches


def main():
    all_matches = []
    processed_files = []

    for filename in SOURCE_FILES:
        try:
            matches = parse_file(filename)
            if matches:
                processed_files.append(filename)
                all_matches.extend(matches)
        except Exception as e:
            print(f" ERROR: {e}")
            import traceback
            traceback.print_exc()

    all_matches = deduplicate(all_matches)

    output = {
        "meta": {
            "generated_at": datetime.now().isoformat(),
            "source_files": processed_files,
            "total_matches": len(all_matches)
        },
        "matches": all_matches
    }

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\nDone! {len(all_matches)} matches saved to {OUTPUT_FILE}")

    years_found = {}
    for m in all_matches:
        yr = m["year"]
        years_found[yr] = years_found.get(yr, 0) + 1
    print("\nMatches per year:")
    for yr in sorted(years_found):
        print(f"  {yr}: {years_found[yr]}")


if __name__ == "__main__":
    main()
