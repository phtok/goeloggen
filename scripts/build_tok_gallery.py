#!/usr/bin/env python3
import csv
import json
import re
from datetime import datetime
from pathlib import Path


def normalize_dashes(value: str) -> str:
    return (value or "").replace("–", "-").replace("—", "-")


def extract_issue_label(value: str) -> str:
    normalized = normalize_dashes(value).replace("_", "-")
    m = re.search(r"(?<!\d)(\d{1,2})-(\d{1,2})(?!\d)", normalized)
    if m:
        return f"{m.group(1)}-{m.group(2)}"
    m = re.search(r"(?<!\d)(\d{1,2})(?!\d)", normalized)
    if m:
        return m.group(1)
    return normalized.strip() or "?"


def compact_issue(issue: str) -> str:
    return extract_issue_label(issue).replace(" ", "")


def issue_sort_key(issue: str) -> int:
    m = re.search(r"\d+", issue or "")
    return int(m.group(0)) if m else 9999


def short_year(year: str) -> str:
    return year[-2:] if len(year) >= 2 else year


def occurrence_suffix(occ: int) -> str:
    if occ <= 0:
        return ""
    letters = "abcdefghijklmnopqrstuvwxyz"
    if occ - 1 < len(letters):
        return letters[occ - 1]
    return f"_{occ}"


def load_entries(csv_path: Path):
    entries = []
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            year = (row.get("jahr") or "").strip()
            issue = (row.get("heft") or "").strip()
            date = (row.get("erscheinung") or "").strip()
            svg = (row.get("svg") or "").strip()
            entry_id = (row.get("id") or "").strip()
            if not year or not svg or not entry_id:
                continue
            issue_label = compact_issue(issue)
            entries.append(
                {
                    "id": entry_id,
                    "year": year,
                    "issue": issue,
                    "issueLabel": issue_label,
                    "issueSort": issue_sort_key(issue),
                    "date": date,
                    "svg": svg,
                }
            )

    entries.sort(key=lambda e: (e["year"], e["issueSort"], e["issue"]))

    seen = {}
    for e in entries:
        key = f"{e['year']}|{e['issueLabel']}"
        occ = seen.get(key, 0)
        seen[key] = occ + 1
        e["code"] = f"J{short_year(e['year'])}H{e['issueLabel']}{occurrence_suffix(occ)}"

    return entries


def build_html(entries):
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    raw_json = json.dumps(entries, ensure_ascii=False)

    template = r'''<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Linienarchiv Philipp Tok</title>
  <style>
    :root {
      --bg: #f4f1e8;
      --bg-soft: #ede7dc;
      --ink: #17140f;
      --muted: #726a5e;
      --line: #d7ccba;
      --accent: #b75c3f;
      --accent-2: #1f6a63;
      --card: #fffdf9;
      --shadow: 0 10px 28px rgba(65, 46, 25, 0.12);
      --shadow-soft: 0 6px 16px rgba(65, 46, 25, 0.08);
    }

    * { box-sizing: border-box; }

    html, body {
      margin: 0;
      padding: 0;
      min-height: 100%;
      color: var(--ink);
      background:
        radial-gradient(1400px 520px at 10% -2%, #f0c29f33, transparent 60%),
        radial-gradient(1200px 420px at 90% 0%, #8bb7a633, transparent 62%),
        linear-gradient(180deg, #faf7f0 0%, var(--bg) 42%, #f6f0e5 100%);
      font-family: "Avenir Next", "Gill Sans", "Trebuchet MS", sans-serif;
    }

    h1, h2, h3 {
      font-family: "Fraunces", "Iowan Old Style", "Palatino Linotype", "Book Antiqua", serif;
      font-weight: 600;
      letter-spacing: 0.01em;
    }

    .shell {
      max-width: 1480px;
      margin: 0 auto;
      padding: 22px 22px 84px;
    }

    .hero {
      position: relative;
      border: 1px solid var(--line);
      border-radius: 18px;
      overflow: hidden;
      background:
        linear-gradient(120deg, #fffbf4 0%, #f6f0e1 48%, #f3efe9 100%);
      box-shadow: var(--shadow);
      padding: 28px 30px 24px;
      margin-bottom: 14px;
      isolation: isolate;
    }

    .hero::before,
    .hero::after {
      content: "";
      position: absolute;
      border-radius: 999px;
      z-index: -1;
      pointer-events: none;
    }

    .hero::before {
      width: 340px;
      height: 340px;
      right: -80px;
      top: -120px;
      background: radial-gradient(circle at 45% 45%, #d4866460, #d4866400 65%);
    }

    .hero::after {
      width: 260px;
      height: 260px;
      left: -90px;
      bottom: -140px;
      background: radial-gradient(circle at 60% 40%, #1f6a6330, #1f6a6300 68%);
    }

    .hero-top {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 24px;
      flex-wrap: wrap;
    }

    .kicker {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 5px 10px;
      border-radius: 999px;
      border: 1px solid #d8c7b4;
      background: #fff8ef;
      color: #5c4a37;
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      margin-bottom: 12px;
    }

    .hero h1 {
      margin: 0;
      font-size: clamp(28px, 5vw, 52px);
      line-height: 1.04;
      max-width: 940px;
    }

    .hero p {
      margin: 12px 0 0;
      max-width: 840px;
      color: #4f493f;
      font-size: 16px;
      line-height: 1.45;
    }

    .hero-actions {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      margin-top: 16px;
    }

    .btn {
      border: 1px solid #c7b9a4;
      background: #fffcf8;
      color: #2f2a23;
      border-radius: 10px;
      padding: 9px 13px;
      cursor: pointer;
      font-size: 13px;
      font-family: inherit;
      text-decoration: none;
      transition: transform 120ms ease, background-color 160ms ease, border-color 160ms ease;
    }

    .btn:hover { background: #fff5e8; border-color: #bfa88d; }
    .btn:active { transform: translateY(1px); }
    .btn.primary {
      background: linear-gradient(180deg, #c86b4e, #b75c3f);
      border-color: #9d4b32;
      color: #fff;
    }
    .btn.primary:hover { background: linear-gradient(180deg, #cc7659, #be6648); }

    .hero-meta {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 10px;
      margin-top: 18px;
    }

    .meta-pill {
      border: 1px solid #d5c8b7;
      background: #fff9f1;
      border-radius: 10px;
      padding: 8px 10px;
      display: grid;
      gap: 2px;
    }

    .meta-pill .label {
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.07em;
      color: #7a6f61;
    }

    .meta-pill .value {
      font-size: 14px;
      color: #2a241d;
      font-weight: 600;
    }

    .controls {
      position: sticky;
      top: 0;
      z-index: 30;
      margin-top: 14px;
      border: 1px solid var(--line);
      border-radius: 14px;
      background: color-mix(in oklab, #fff 86%, #f6ecde 14%);
      box-shadow: var(--shadow-soft);
      backdrop-filter: blur(10px);
      padding: 12px;
      display: grid;
      gap: 10px;
    }

    .controls-line {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }

    .mode-switch {
      display: inline-flex;
      border: 1px solid #d6c8b4;
      border-radius: 10px;
      overflow: hidden;
      background: #fffaf3;
    }

    .mode-switch button {
      border: 0;
      border-right: 1px solid #dfd2c2;
      padding: 8px 11px;
      font-size: 12px;
      background: transparent;
      color: #584f43;
      cursor: pointer;
      font-family: inherit;
      transition: background-color 140ms ease, color 140ms ease;
    }

    .mode-switch button:last-child { border-right: 0; }
    .mode-switch button.active {
      background: #2f2b24;
      color: #fff;
    }

    .search-wrap {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 7px 10px;
      border: 1px solid #d7cab9;
      border-radius: 10px;
      background: #fffefb;
      min-width: 240px;
      flex: 1 1 320px;
    }

    .search-wrap input {
      border: 0;
      background: transparent;
      outline: none;
      width: 100%;
      font-size: 14px;
      color: #2e281f;
      font-family: inherit;
    }

    .select {
      border: 1px solid #d6c8b5;
      border-radius: 10px;
      padding: 7px 10px;
      font-size: 13px;
      background: #fffefb;
      color: #3d352c;
      font-family: inherit;
    }

    .toggle {
      display: inline-flex;
      align-items: center;
      gap: 7px;
      font-size: 13px;
      color: #4f463c;
      white-space: nowrap;
      padding: 7px 9px;
      border: 1px solid #d8ccba;
      border-radius: 10px;
      background: #fffefb;
    }

    .toggle input { margin: 0; }

    .year-chips {
      display: flex;
      gap: 6px;
      overflow-x: auto;
      padding-bottom: 2px;
      scrollbar-width: thin;
    }

    .year-chip {
      border: 1px solid #d5c8b5;
      border-radius: 999px;
      background: #fff8ef;
      color: #584c3c;
      font-size: 12px;
      padding: 5px 10px;
      cursor: pointer;
      white-space: nowrap;
      font-family: inherit;
      transition: all 140ms ease;
    }

    .year-chip.active {
      background: #1f6a63;
      color: #f4fffd;
      border-color: #11514b;
    }

    .status-line {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      margin: 16px 2px 10px;
      color: #584f44;
      font-size: 13px;
      flex-wrap: wrap;
    }

    .status-line strong { color: #1e1a15; }

    .view {
      display: none;
      animation: fade-in 260ms ease;
    }

    .view.active { display: block; }

    .empty-state {
      border: 1px dashed #cbbca8;
      border-radius: 14px;
      padding: 30px 18px;
      text-align: center;
      color: #6b6155;
      background: #fff9f1;
    }

    .mosaic-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(170px, 1fr));
      gap: 12px;
    }

    .glyph-card {
      border: 1px solid var(--line);
      border-radius: 14px;
      background: var(--card);
      box-shadow: var(--shadow-soft);
      padding: 8px;
      display: grid;
      gap: 7px;
      transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease;
      animation: card-in 440ms ease both;
      animation-delay: var(--delay, 0ms);
    }

    .glyph-card:hover {
      transform: translateY(-2px);
      box-shadow: 0 14px 30px rgba(79, 57, 31, 0.16);
      border-color: #c6b099;
    }

    .glyph-card.is-selected {
      border-color: #1f6a63;
      background: #f2fbf9;
    }

    .card-image-btn {
      border: 0;
      padding: 0;
      background: #f7f2e8;
      border-radius: 10px;
      min-height: 140px;
      display: grid;
      place-items: center;
      cursor: zoom-in;
      overflow: hidden;
    }

    .card-image-btn img {
      width: 100%;
      height: 138px;
      object-fit: contain;
      display: block;
      transition: transform 220ms ease;
    }

    .glyph-card:hover .card-image-btn img {
      transform: scale(1.04);
    }

    .card-meta {
      display: grid;
      gap: 2px;
      min-height: 48px;
    }

    .card-code {
      font-family: "Avenir Next Condensed", "Avenir Next", sans-serif;
      font-size: 13px;
      letter-spacing: 0.06em;
      color: #2b5d59;
      text-transform: uppercase;
      font-weight: 700;
    }

    .card-info {
      font-size: 12px;
      color: #5f564a;
      line-height: 1.35;
    }

    .card-tools {
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 6px;
    }

    .mini-btn {
      border: 1px solid #d4c8b8;
      border-radius: 9px;
      background: #fff;
      color: #3d352b;
      padding: 6px 8px;
      font-size: 12px;
      cursor: pointer;
      font-family: inherit;
      text-align: center;
      text-decoration: none;
    }

    .mini-btn:hover { background: #fff4e6; }

    .pin-toggle.active {
      background: #1f6a63;
      border-color: #11524d;
      color: #effdfa;
    }

    .timeline-stack {
      display: grid;
      gap: 14px;
    }

    .timeline-row {
      border: 1px solid var(--line);
      border-radius: 14px;
      background: #fffcf7;
      box-shadow: var(--shadow-soft);
      overflow: hidden;
    }

    .timeline-head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      padding: 10px 12px;
      border-bottom: 1px solid #eadfce;
      background: linear-gradient(90deg, #fff7ea, #fffdf8 70%);
    }

    .timeline-head h3 {
      margin: 0;
      font-size: 18px;
    }

    .timeline-count {
      font-size: 12px;
      color: #6f6559;
    }

    .timeline-track {
      display: grid;
      grid-auto-flow: column;
      grid-auto-columns: minmax(180px, 220px);
      gap: 10px;
      overflow-x: auto;
      scroll-snap-type: x mandatory;
      padding: 12px;
      scrollbar-width: thin;
    }

    .timeline-track .glyph-card {
      scroll-snap-align: start;
      margin-bottom: 2px;
    }

    .field-wrap {
      border: 1px solid var(--line);
      border-radius: 14px;
      background: #fffcf6;
      box-shadow: var(--shadow);
      overflow: hidden;
    }

    .field-tools {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
      padding: 10px;
      border-bottom: 1px solid #eadfce;
      background: linear-gradient(90deg, #fff7ec, #fffdf8);
    }

    .field-tools output {
      min-width: 46px;
      text-align: right;
      font-size: 13px;
      color: #584f43;
    }

    .field-viewport {
      height: min(72vh, 780px);
      overflow: auto;
      position: relative;
      cursor: grab;
      background:
        linear-gradient(180deg, #f9f2e7 0%, #fffdf9 65%),
        repeating-linear-gradient(90deg, #f0e5d5 0, #f0e5d5 1px, transparent 1px, transparent 36px),
        repeating-linear-gradient(0deg, #f7efe3 0, #f7efe3 1px, transparent 1px, transparent 36px);
      touch-action: none;
    }

    .field-viewport.dragging { cursor: grabbing; }

    .field-stage {
      position: relative;
      transform-origin: left top;
      will-change: transform;
    }

    .field-lane {
      position: absolute;
      top: 0;
      bottom: 0;
      width: 190px;
      border-left: 1px solid #d8cbb8;
      border-right: 1px solid #d8cbb8;
      background: linear-gradient(180deg, #ffffff50 0%, #ffffff24 100%);
    }

    .field-lane span {
      position: sticky;
      top: 8px;
      left: 8px;
      display: inline-block;
      padding: 3px 7px;
      border-radius: 999px;
      background: #fff8ed;
      border: 1px solid #d2c3ad;
      color: #635849;
      font-size: 11px;
      letter-spacing: 0.05em;
      text-transform: uppercase;
      z-index: 2;
    }

    .field-node {
      position: absolute;
      width: 96px;
      border: 1px solid #d8c9b4;
      border-radius: 10px;
      background: #fffdf8;
      box-shadow: 0 7px 15px rgba(58, 43, 27, 0.14);
      padding: 5px;
      cursor: pointer;
      text-align: left;
      transition: transform 160ms ease, box-shadow 160ms ease, border-color 160ms ease;
    }

    .field-node:hover {
      transform: translateY(-2px) scale(1.03);
      box-shadow: 0 10px 20px rgba(58, 43, 27, 0.2);
      z-index: 3;
    }

    .field-node.is-selected {
      border-color: #1f6a63;
      background: #f2fbf9;
    }

    .field-node img {
      width: 100%;
      height: 56px;
      object-fit: contain;
      display: block;
      background: #f8f3ea;
      border-radius: 6px;
      pointer-events: none;
    }

    .field-node span {
      display: block;
      margin-top: 4px;
      font-size: 10px;
      color: #554c40;
      letter-spacing: 0.03em;
      pointer-events: none;
      font-weight: 600;
    }

    .compare-wrap {
      border: 1px solid var(--line);
      border-radius: 14px;
      background: #fffcf6;
      box-shadow: var(--shadow);
      overflow: hidden;
    }

    .compare-tools {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
      padding: 10px;
      border-bottom: 1px solid #eadfce;
      background: linear-gradient(90deg, #fff7ea, #fffdf8);
    }

    .compare-grid {
      padding: 12px;
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(270px, 1fr));
      gap: 12px;
    }

    .compare-card {
      border: 1px solid #d7cab8;
      border-radius: 12px;
      background: #fff;
      box-shadow: var(--shadow-soft);
      display: grid;
      overflow: hidden;
    }

    .compare-head {
      padding: 8px 10px;
      border-bottom: 1px solid #ece0cf;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
    }

    .compare-title {
      font-size: 12px;
      line-height: 1.3;
      color: #473d31;
    }

    .compare-stage {
      position: relative;
      height: 280px;
      overflow: auto;
      background: #f7f1e6;
    }

    .compare-inner {
      min-width: 320px;
      min-height: 320px;
      display: grid;
      place-items: center;
      transform-origin: center center;
      transition: transform 140ms ease;
    }

    .compare-inner img {
      width: 280px;
      height: 280px;
      object-fit: contain;
      display: block;
      background: #fff;
      border-radius: 8px;
      box-shadow: 0 5px 14px rgba(67, 49, 30, 0.11);
      user-select: none;
      pointer-events: none;
    }

    .compare-meta {
      padding: 7px 10px 10px;
      font-size: 11px;
      color: #5b5146;
      border-top: 1px solid #ece0cf;
      line-height: 1.35;
    }

    .selection-dock {
      position: fixed;
      right: 18px;
      bottom: 18px;
      z-index: 34;
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
      border: 1px solid #c4b29a;
      border-radius: 14px;
      background: #fff8ee;
      box-shadow: 0 14px 30px rgba(58, 42, 23, 0.24);
      padding: 10px;
      max-width: min(700px, calc(100vw - 26px));
    }

    .dock-count {
      font-size: 12px;
      color: #5f5448;
      padding-right: 4px;
      white-space: nowrap;
    }

    .detail-pane {
      position: fixed;
      right: 0;
      top: 0;
      bottom: 0;
      width: min(540px, 96vw);
      transform: translateX(102%);
      transition: transform 260ms cubic-bezier(.23,.75,.24,1);
      z-index: 45;
      background: #fffdf9;
      border-left: 1px solid #d7cab7;
      box-shadow: -16px 0 34px rgba(53, 38, 22, 0.22);
      display: grid;
      grid-template-rows: auto auto 1fr auto;
    }

    .detail-pane.open { transform: translateX(0); }

    .detail-head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      padding: 12px;
      border-bottom: 1px solid #ebe0cf;
      background: #fff7ea;
    }

    .detail-head h3 {
      margin: 0;
      font-size: 18px;
    }

    .detail-nav {
      padding: 8px 12px;
      display: flex;
      align-items: center;
      gap: 6px;
      border-bottom: 1px solid #eee3d4;
    }

    .detail-image {
      margin: 12px;
      border: 1px solid #ddd0bd;
      border-radius: 12px;
      background: #f8f1e5;
      display: grid;
      place-items: center;
      min-height: 280px;
    }

    .detail-image img {
      width: calc(100% - 20px);
      height: 320px;
      object-fit: contain;
      display: block;
    }

    .detail-meta {
      padding: 0 14px 14px;
      font-size: 13px;
      line-height: 1.45;
      color: #4b4236;
      display: grid;
      gap: 5px;
    }

    .detail-foot {
      border-top: 1px solid #ece0cf;
      padding: 10px 12px;
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      background: #fff8ef;
    }

    @keyframes fade-in {
      from { opacity: 0; transform: translateY(4px); }
      to { opacity: 1; transform: none; }
    }

    @keyframes card-in {
      from { opacity: 0; transform: translateY(8px) scale(0.99); }
      to { opacity: 1; transform: translateY(0) scale(1); }
    }

    @media (max-width: 1024px) {
      .shell { padding: 14px 12px 92px; }
      .hero { padding: 18px 16px 16px; }
      .controls { top: 4px; }
      .selection-dock { right: 10px; left: 10px; bottom: 10px; }
    }

    @media (max-width: 700px) {
      .hero h1 { line-height: 1.08; }
      .mosaic-grid { grid-template-columns: repeat(auto-fill, minmax(145px, 1fr)); }
      .timeline-track { grid-auto-columns: minmax(154px, 184px); }
      .field-node { width: 88px; }
      .field-node img { height: 50px; }
      .compare-grid { grid-template-columns: 1fr; }
      .detail-image img { height: 260px; }
    }
  </style>
</head>
<body>
  <div class="shell">
    <header class="hero">
      <div class="hero-top">
        <div>
          <div class="kicker">Linienarchiv · lebendige Sammlung</div>
          <h1>Philipp-Tok-Zeichnungen als Erlebnisgalerie</h1>
          <p>
            Studieren, vergleichen, wiederfinden: Diese Oberfläche ist auf Blickrhythmus ausgelegt.
            Statt einer bloßen Liste bekommst du drei Bewegungsformen: Mosaik, horizontale Zeitbahn und ein zoombares Sammlungsfeld.
          </p>
          <div class="hero-actions">
            <button class="btn primary" id="heroCompare">Vergleichsansicht öffnen</button>
            <button class="btn" id="heroDownloadList">Merkliste als TXT</button>
            <button class="btn" id="heroShare">Merkliste-Link kopieren</button>
          </div>
        </div>
      </div>
      <div class="hero-meta">
        <div class="meta-pill"><span class="label">Erzeugt</span><span class="value">__GENERATED_AT__</span></div>
        <div class="meta-pill"><span class="label">Einträge</span><span class="value" id="metaTotal">0</span></div>
        <div class="meta-pill"><span class="label">Sichtbar</span><span class="value" id="metaVisible">0</span></div>
        <div class="meta-pill"><span class="label">Gemerkte Auswahl</span><span class="value" id="metaSelected">0</span></div>
      </div>
    </header>

    <section class="controls" aria-label="Filter und Ansichten">
      <div class="controls-line">
        <div class="mode-switch" role="tablist" aria-label="Ansicht wechseln">
          <button class="active" data-view="mosaic">Mosaik</button>
          <button data-view="timeline">Zeitbahn</button>
          <button data-view="field">Sammlungsfeld</button>
          <button data-view="compare">Vergleich</button>
        </div>

        <label class="search-wrap">
          <span>Suche</span>
          <input id="queryInput" type="search" placeholder="J25H12, Heft 47, 2018, ID ..." autocomplete="off">
        </label>

        <select class="select" id="sortSelect" aria-label="Sortierung">
          <option value="chrono-asc">Chronologisch aufsteigend</option>
          <option value="chrono-desc">Chronologisch absteigend</option>
          <option value="code">Code (J..H..)</option>
          <option value="focus">Fokus auf aktuelle Jahre</option>
        </select>

        <label class="toggle"><input id="onlySelectedToggle" type="checkbox"> Nur Merkliste</label>
      </div>

      <div class="controls-line">
        <button class="btn" id="selectAllVisible">Sichtbare merken</button>
        <button class="btn" id="clearSelection">Merkliste leeren</button>
        <button class="btn" id="downloadSelection">Merkliste als TXT</button>
        <button class="btn" id="copySelectionIds">IDs kopieren</button>
      </div>

      <div class="year-chips" id="yearChips"></div>
    </section>

    <div class="status-line">
      <div>
        <strong id="statusHeadline">Lade Daten …</strong>
        <span id="statusSub">Filter auf deine Sammlung anwenden.</span>
      </div>
      <div id="activeModeLabel">Ansicht: Mosaik</div>
    </div>

    <main>
      <section class="view active" id="mosaicView" aria-label="Mosaikansicht"></section>
      <section class="view" id="timelineView" aria-label="Zeitbahnansicht"></section>
      <section class="view" id="fieldView" aria-label="Sammlungsfeldansicht">
        <div class="field-wrap">
          <div class="field-tools">
            <button class="btn" id="fieldZoomOut">−</button>
            <input id="fieldZoomRange" type="range" min="55" max="240" value="100">
            <button class="btn" id="fieldZoomIn">+</button>
            <button class="btn" id="fieldZoomReset">Reset</button>
            <output id="fieldZoomOutLabel">100%</output>
            <span style="color:#685f53;font-size:12px;">Tipp: Fläche ziehen, um zu navigieren.</span>
          </div>
          <div class="field-viewport" id="fieldViewport">
            <div class="field-stage" id="fieldStage"></div>
          </div>
        </div>
      </section>
      <section class="view" id="compareView" aria-label="Vergleichsansicht">
        <div class="compare-wrap">
          <div class="compare-tools">
            <button class="btn" id="compareSyncBtn">Sync-Pan: aktiv</button>
            <label class="toggle">
              Zoom
              <input id="compareZoomRange" type="range" min="70" max="280" value="100">
            </label>
            <output id="compareZoomLabel">100%</output>
            <span style="color:#6f6458;font-size:12px;">Vergleich funktioniert am besten mit 2-6 Zeichnungen.</span>
          </div>
          <div class="compare-grid" id="compareGrid"></div>
        </div>
      </section>
    </main>
  </div>

  <aside class="detail-pane" id="detailPane" aria-label="Detailansicht">
    <div class="detail-head">
      <h3 id="detailTitle">Details</h3>
      <button class="btn" id="detailClose">Schließen</button>
    </div>
    <div class="detail-nav">
      <button class="btn" id="detailPrev">← Vorherige</button>
      <button class="btn" id="detailNext">Nächste →</button>
      <span id="detailPos" style="font-size:12px;color:#6a5f53;"></span>
    </div>
    <div class="detail-image"><img id="detailImg" alt="Detailzeichnung"></div>
    <div class="detail-meta" id="detailMeta"></div>
    <div class="detail-foot">
      <button class="btn" id="detailToggle">Merken</button>
      <a class="btn" id="detailDownload" href="#" download>SVG herunterladen</a>
    </div>
  </aside>

  <div class="selection-dock" id="selectionDock">
    <span class="dock-count" id="dockCount">0 gemerkt</span>
    <button class="btn primary" id="dockCompare">Vergleichen</button>
    <button class="btn" id="dockDownload">Merkliste TXT</button>
    <button class="btn" id="dockClear">Leeren</button>
  </div>

  <script>
    const RAW_ENTRIES = __RAW_ENTRIES__;

    const STORAGE_KEY = "tok_gallery_selection_v1";
    const VIEW_NAMES = {
      mosaic: "Mosaik",
      timeline: "Zeitbahn",
      field: "Sammlungsfeld",
      compare: "Vergleich"
    };

    const state = {
      entries: [],
      filtered: [],
      years: [],
      selected: new Set(),
      activeYears: new Set(),
      query: "",
      view: "mosaic",
      sort: "chrono-asc",
      onlySelected: false,
      compareZoom: 1,
      compareSync: true,
      fieldZoom: 1,
      detailId: null,
      fieldDrag: null,
      fieldSyncing: false,
      compareSyncing: false
    };

    const els = {
      metaTotal: document.getElementById("metaTotal"),
      metaVisible: document.getElementById("metaVisible"),
      metaSelected: document.getElementById("metaSelected"),
      queryInput: document.getElementById("queryInput"),
      sortSelect: document.getElementById("sortSelect"),
      onlySelectedToggle: document.getElementById("onlySelectedToggle"),
      yearChips: document.getElementById("yearChips"),
      statusHeadline: document.getElementById("statusHeadline"),
      statusSub: document.getElementById("statusSub"),
      activeModeLabel: document.getElementById("activeModeLabel"),
      mosaicView: document.getElementById("mosaicView"),
      timelineView: document.getElementById("timelineView"),
      fieldView: document.getElementById("fieldView"),
      compareView: document.getElementById("compareView"),
      fieldViewport: document.getElementById("fieldViewport"),
      fieldStage: document.getElementById("fieldStage"),
      fieldZoomRange: document.getElementById("fieldZoomRange"),
      fieldZoomOutLabel: document.getElementById("fieldZoomOutLabel"),
      compareGrid: document.getElementById("compareGrid"),
      compareZoomRange: document.getElementById("compareZoomRange"),
      compareZoomLabel: document.getElementById("compareZoomLabel"),
      compareSyncBtn: document.getElementById("compareSyncBtn"),
      detailPane: document.getElementById("detailPane"),
      detailTitle: document.getElementById("detailTitle"),
      detailImg: document.getElementById("detailImg"),
      detailMeta: document.getElementById("detailMeta"),
      detailToggle: document.getElementById("detailToggle"),
      detailDownload: document.getElementById("detailDownload"),
      detailPrev: document.getElementById("detailPrev"),
      detailNext: document.getElementById("detailNext"),
      detailPos: document.getElementById("detailPos"),
      selectionDock: document.getElementById("selectionDock"),
      dockCount: document.getElementById("dockCount")
    };

    function loadSelection() {
      try {
        const raw = localStorage.getItem(STORAGE_KEY);
        if (!raw) return new Set();
        const arr = JSON.parse(raw);
        return new Set(Array.isArray(arr) ? arr : []);
      } catch {
        return new Set();
      }
    }

    function saveSelection() {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(Array.from(state.selected).sort()));
    }

    function hashNumber(str) {
      let h = 2166136261;
      for (let i = 0; i < str.length; i += 1) {
        h ^= str.charCodeAt(i);
        h = Math.imul(h, 16777619);
      }
      return (h >>> 0);
    }

    function escapeHTML(value) {
      return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/\"/g, "&quot;")
        .replace(/'/g, "&#39;");
    }

    function sanitizeFileName(value) {
      const cleaned = String(value || "").replace(/[^A-Za-z0-9._-]+/g, "_").replace(/^_+|_+$/g, "");
      return cleaned || "zeichnung";
    }

    function findEntryById(id) {
      return state.entries.find(e => e.id === id) || null;
    }

    function isSelected(id) {
      return state.selected.has(id);
    }

    function toggleSelected(id, force) {
      if (!id) return;
      const shouldSelect = typeof force === "boolean" ? force : !state.selected.has(id);
      if (shouldSelect) state.selected.add(id); else state.selected.delete(id);
      saveSelection();
      renderAll();
    }

    function visibleListSorted(list) {
      const copy = list.slice();
      const cmpChrono = (a, b) => {
        const ay = Number(a.year), by = Number(b.year);
        if (ay !== by) return ay - by;
        if (a.issueSort !== b.issueSort) return a.issueSort - b.issueSort;
        return a.issue.localeCompare(b.issue, "de");
      };
      switch (state.sort) {
        case "chrono-desc":
          copy.sort((a, b) => -cmpChrono(a, b));
          break;
        case "code":
          copy.sort((a, b) => a.code.localeCompare(b.code, "de"));
          break;
        case "focus":
          copy.sort((a, b) => {
            const byYear = Number(b.year) - Number(a.year);
            if (byYear !== 0) return byYear;
            if (a.issueSort !== b.issueSort) return a.issueSort - b.issueSort;
            return a.code.localeCompare(b.code, "de");
          });
          break;
        default:
          copy.sort(cmpChrono);
      }
      return copy;
    }

    function applyFilters() {
      const q = state.query.trim().toLowerCase();
      let list = state.entries.filter(e => state.activeYears.has(e.year));

      if (q) {
        list = list.filter(e => {
          const hay = `${e.id} ${e.code} ${e.year} ${e.issue} ${e.date}`.toLowerCase();
          return hay.includes(q);
        });
      }

      if (state.onlySelected) {
        list = list.filter(e => state.selected.has(e.id));
      }

      state.filtered = visibleListSorted(list);
    }

    function cardHTML(entry, idx, variant) {
      const selected = isSelected(entry.id);
      const delay = (idx % 18) * 18;
      const variantClass = variant === "timeline" ? "timeline-card" : "";
      return `
        <article class="glyph-card ${variantClass} ${selected ? "is-selected" : ""}" data-id="${escapeHTML(entry.id)}" style="--delay:${delay}ms;">
          <button class="card-image-btn" data-action="detail" data-id="${escapeHTML(entry.id)}">
            <img src="${escapeHTML(entry.svg)}" alt="${escapeHTML(entry.code)}" loading="lazy">
          </button>
          <div class="card-meta">
            <div class="card-code">${escapeHTML(entry.code)}</div>
            <div class="card-info">${escapeHTML(entry.year)} · H${escapeHTML(entry.issueLabel)} · ${escapeHTML(entry.date || "")}</div>
          </div>
          <div class="card-tools">
            <button class="mini-btn pin-toggle ${selected ? "active" : ""}" data-action="toggle" data-id="${escapeHTML(entry.id)}">${selected ? "Gemerkt" : "Merken"}</button>
            <a class="mini-btn" href="${escapeHTML(entry.svg)}" download="${escapeHTML(sanitizeFileName(entry.code + ".svg"))}">SVG</a>
          </div>
        </article>
      `;
    }

    function emptyHTML(text) {
      return `<div class="empty-state">${escapeHTML(text)}</div>`;
    }

    function renderMosaic() {
      if (!state.filtered.length) {
        els.mosaicView.innerHTML = emptyHTML("Keine Zeichnungen für diese Filterkombination.");
        return;
      }
      const cards = state.filtered.map((e, i) => cardHTML(e, i, "mosaic")).join("");
      els.mosaicView.innerHTML = `<div class="mosaic-grid">${cards}</div>`;
    }

    function renderTimeline() {
      if (!state.filtered.length) {
        els.timelineView.innerHTML = emptyHTML("Keine Zeichnungen für diese Filterkombination.");
        return;
      }

      const byYear = new Map();
      for (const e of state.filtered) {
        if (!byYear.has(e.year)) byYear.set(e.year, []);
        byYear.get(e.year).push(e);
      }

      const rows = Array.from(byYear.entries())
        .sort((a, b) => Number(a[0]) - Number(b[0]))
        .map(([year, list]) => {
          const cards = list.map((e, i) => cardHTML(e, i, "timeline")).join("");
          return `
            <section class="timeline-row">
              <header class="timeline-head">
                <h3>${escapeHTML(year)}</h3>
                <div class="timeline-count">${list.length} Einträge</div>
              </header>
              <div class="timeline-track">${cards}</div>
            </section>
          `;
        }).join("");

      els.timelineView.innerHTML = `<div class="timeline-stack">${rows}</div>`;
    }

    function renderField() {
      if (!state.filtered.length) {
        els.fieldStage.innerHTML = emptyHTML("Keine Zeichnungen für diese Filterkombination.");
        els.fieldStage.style.width = "100%";
        els.fieldStage.style.height = "100%";
        return;
      }

      const years = Array.from(new Set(state.filtered.map(e => e.year))).sort((a, b) => Number(a) - Number(b));
      const laneGap = 230;
      const laneWidth = 190;
      const stageWidth = Math.max(2200, years.length * laneGap + 360);
      const stageHeight = 1920;

      const yearIndex = new Map(years.map((y, i) => [y, i]));

      const lanes = years.map(y => {
        const idx = yearIndex.get(y) || 0;
        const x = 110 + idx * laneGap;
        return `<div class="field-lane" style="left:${x}px;"><span>${escapeHTML(y)}</span></div>`;
      }).join("");

      const nodes = state.filtered.map((e) => {
        const idx = yearIndex.get(e.year) || 0;
        const h = hashNumber(e.id);
        const jitterX = (h % 68) - 34;
        const jitterY = ((Math.floor(h / 71) % 84) - 42);
        const issueFrac = Math.min(1, Math.max(0, (e.issueSort || 1) / 53));
        const x = 158 + idx * laneGap + jitterX;
        const y = 80 + issueFrac * 1620 + jitterY;
        const selected = isSelected(e.id) ? "is-selected" : "";
        return `
          <button class="field-node ${selected}" data-id="${escapeHTML(e.id)}" data-action="detail" style="left:${x}px;top:${y}px;">
            <img src="${escapeHTML(e.svg)}" alt="${escapeHTML(e.code)}" loading="lazy">
            <span>${escapeHTML(e.code)}</span>
          </button>
        `;
      }).join("");

      els.fieldStage.style.width = `${stageWidth}px`;
      els.fieldStage.style.height = `${stageHeight}px`;
      els.fieldStage.innerHTML = lanes + nodes;
      applyFieldZoom(false);
    }

    function selectedEntries() {
      const all = state.entries.filter(e => state.selected.has(e.id));
      return visibleListSorted(all);
    }

    function renderCompare() {
      const selected = selectedEntries();
      if (!selected.length) {
        els.compareGrid.innerHTML = emptyHTML("Wähle Zeichnungen mit \"Merken\" aus. Danach erscheinen sie hier für den direkten Vergleich.");
        return;
      }

      const panes = selected.map((e) => {
        return `
          <article class="compare-card" data-id="${escapeHTML(e.id)}">
            <div class="compare-head">
              <div class="compare-title"><strong>${escapeHTML(e.code)}</strong><br>${escapeHTML(e.year)} · H${escapeHTML(e.issueLabel)}</div>
              <button class="mini-btn" data-action="toggle" data-id="${escapeHTML(e.id)}">Entfernen</button>
            </div>
            <div class="compare-stage" data-compare-scroll="${escapeHTML(e.id)}">
              <div class="compare-inner" style="transform:scale(${state.compareZoom});">
                <img src="${escapeHTML(e.svg)}" alt="${escapeHTML(e.code)}" loading="lazy">
              </div>
            </div>
            <div class="compare-meta">${escapeHTML(e.date || "")}</div>
          </article>
        `;
      }).join("");

      els.compareGrid.innerHTML = panes;
      bindCompareScrollSync();
    }

    function renderYearChips() {
      const chips = [];
      const allActive = state.activeYears.size === state.years.length;
      chips.push(`<button class="year-chip ${allActive ? "active" : ""}" data-year="__all">Alle</button>`);

      for (const y of state.years) {
        const active = state.activeYears.has(y) ? "active" : "";
        chips.push(`<button class="year-chip ${active}" data-year="${escapeHTML(y)}">${escapeHTML(y)}</button>`);
      }

      els.yearChips.innerHTML = chips.join("");
    }

    function setView(view) {
      state.view = view;
      for (const btn of document.querySelectorAll(".mode-switch button")) {
        btn.classList.toggle("active", btn.getAttribute("data-view") === view);
      }
      for (const panel of document.querySelectorAll(".view")) {
        panel.classList.toggle("active", panel.id === `${view}View`);
      }
      els.activeModeLabel.textContent = `Ansicht: ${VIEW_NAMES[view] || view}`;

      if (view === "compare") renderCompare();
      if (view === "field") renderField();
    }

    function updateStatus() {
      const visible = state.filtered.length;
      const total = state.entries.length;
      const sel = state.selected.size;

      els.metaTotal.textContent = String(total);
      els.metaVisible.textContent = String(visible);
      els.metaSelected.textContent = String(sel);
      els.statusHeadline.textContent = `${visible} von ${total} Zeichnungen sichtbar`;
      els.statusSub.textContent = state.onlySelected
        ? "Nur deine Merkliste ist aktiv."
        : "Klick auf eine Zeichnung für Detailansicht und Kontext.";

      els.dockCount.textContent = `${sel} gemerkt`;
    }

    function openDetail(id) {
      const entry = findEntryById(id);
      if (!entry) return;
      state.detailId = id;
      renderDetail();
      els.detailPane.classList.add("open");
    }

    function closeDetail() {
      els.detailPane.classList.remove("open");
    }

    function detailContextList() {
      if (state.filtered.length) return state.filtered;
      return state.entries;
    }

    function renderDetail() {
      const entry = findEntryById(state.detailId);
      if (!entry) {
        closeDetail();
        return;
      }

      const ctx = detailContextList();
      const idx = Math.max(0, ctx.findIndex(e => e.id === entry.id));
      const pos = `${idx + 1}/${ctx.length}`;

      els.detailTitle.textContent = entry.code;
      els.detailImg.src = entry.svg;
      els.detailImg.alt = entry.code;
      els.detailMeta.innerHTML = `
        <div><strong>Jahr:</strong> ${escapeHTML(entry.year)}</div>
        <div><strong>Heft:</strong> ${escapeHTML(entry.issue)} (${escapeHTML(entry.issueLabel)})</div>
        <div><strong>Datum:</strong> ${escapeHTML(entry.date || "-")}</div>
        <div><strong>ID:</strong> <code>${escapeHTML(entry.id)}</code></div>
      `;
      els.detailPos.textContent = pos;
      const selected = isSelected(entry.id);
      els.detailToggle.textContent = selected ? "Aus Merkliste entfernen" : "Zur Merkliste";
      els.detailToggle.classList.toggle("primary", selected);
      els.detailToggle.setAttribute("data-id", entry.id);
      els.detailDownload.href = entry.svg;
      els.detailDownload.download = sanitizeFileName(`${entry.code}.svg`);

      const prev = ctx[idx - 1];
      const next = ctx[idx + 1];
      els.detailPrev.disabled = !prev;
      els.detailNext.disabled = !next;
      els.detailPrev.setAttribute("data-id", prev ? prev.id : "");
      els.detailNext.setAttribute("data-id", next ? next.id : "");
    }

    function downloadText(filename, text) {
      const blob = new Blob([text], { type: "text/plain;charset=utf-8" });
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      setTimeout(() => URL.revokeObjectURL(a.href), 600);
    }

    function selectionTxt() {
      const sel = selectedEntries();
      if (!sel.length) return "";
      const lines = sel.map(e => `${e.code}\t${e.year}\tH${e.issueLabel}\t${e.date || ""}\t${e.id}\t${e.svg}`);
      return lines.join("\n") + "\n";
    }

    async function copySelectionIds() {
      const ids = selectedEntries().map(e => e.id).join("\n");
      if (!ids) return;
      try {
        await navigator.clipboard.writeText(ids + "\n");
      } catch {
        downloadText("selection_ids.txt", ids + "\n");
      }
    }

    async function copyShareLink() {
      const ids = selectedEntries().map(e => e.id);
      if (!ids.length) return;
      const base = String(location.href).split("?")[0].split("#")[0];
      const link = `${base}?sel=${encodeURIComponent(ids.join(","))}`;
      try {
        await navigator.clipboard.writeText(link);
      } catch {
        downloadText("selection_link.txt", link + "\n");
      }
    }

    function preloadSelectionFromURL() {
      const sp = new URLSearchParams(location.search);
      const sel = (sp.get("sel") || "").trim();
      if (!sel) return;
      for (const id of sel.split(",")) {
        const clean = id.trim();
        if (clean) state.selected.add(clean);
      }
    }

    function bindSharedEvents(container) {
      container.addEventListener("click", (ev) => {
        const actionTarget = ev.target.closest("[data-action]");
        if (!actionTarget) return;
        const action = actionTarget.getAttribute("data-action");
        const id = actionTarget.getAttribute("data-id") || actionTarget.closest("[data-id]")?.getAttribute("data-id");
        if (!action || !id) return;

        if (action === "toggle") {
          toggleSelected(id);
          return;
        }
        if (action === "detail") {
          openDetail(id);
        }
      });
    }

    function bindCompareScrollSync() {
      const scrollers = Array.from(els.compareGrid.querySelectorAll("[data-compare-scroll]"));
      for (const scroller of scrollers) {
        scroller.addEventListener("scroll", () => {
          if (!state.compareSync || state.compareSyncing) return;
          state.compareSyncing = true;
          const sx = scroller.scrollWidth - scroller.clientWidth;
          const sy = scroller.scrollHeight - scroller.clientHeight;
          const rx = sx > 0 ? scroller.scrollLeft / sx : 0;
          const ry = sy > 0 ? scroller.scrollTop / sy : 0;
          for (const other of scrollers) {
            if (other === scroller) continue;
            const ox = other.scrollWidth - other.clientWidth;
            const oy = other.scrollHeight - other.clientHeight;
            other.scrollLeft = Math.round(rx * Math.max(0, ox));
            other.scrollTop = Math.round(ry * Math.max(0, oy));
          }
          state.compareSyncing = false;
        }, { passive: true });
      }
    }

    function applyFieldZoom(updateControl = true, anchorX = null, anchorY = null) {
      const viewport = els.fieldViewport;
      const stage = els.fieldStage;
      const prev = Number(stage.dataset.zoom || "1") || 1;
      const next = Math.max(0.55, Math.min(2.4, state.fieldZoom));
      const cx = anchorX == null ? viewport.clientWidth / 2 : anchorX;
      const cy = anchorY == null ? viewport.clientHeight / 2 : anchorY;
      const worldX = (viewport.scrollLeft + cx) / prev;
      const worldY = (viewport.scrollTop + cy) / prev;

      stage.style.transform = `scale(${next})`;
      stage.dataset.zoom = String(next);

      viewport.scrollLeft = worldX * next - cx;
      viewport.scrollTop = worldY * next - cy;

      if (updateControl) {
        els.fieldZoomRange.value = String(Math.round(next * 100));
      }
      els.fieldZoomOutLabel.textContent = `${Math.round(next * 100)}%`;
    }

    function renderAll() {
      applyFilters();
      renderYearChips();
      renderMosaic();
      renderTimeline();
      if (state.view === "field") renderField();
      if (state.view === "compare") renderCompare();
      if (state.detailId) renderDetail();
      updateStatus();
    }

    function setupControls() {
      bindSharedEvents(els.mosaicView);
      bindSharedEvents(els.timelineView);
      bindSharedEvents(els.fieldStage);
      bindSharedEvents(els.compareGrid);

      els.queryInput.addEventListener("input", () => {
        state.query = els.queryInput.value || "";
        renderAll();
      });

      els.sortSelect.addEventListener("change", () => {
        state.sort = els.sortSelect.value;
        renderAll();
      });

      els.onlySelectedToggle.addEventListener("change", () => {
        state.onlySelected = els.onlySelectedToggle.checked;
        renderAll();
      });

      els.yearChips.addEventListener("click", (ev) => {
        const chip = ev.target.closest(".year-chip");
        if (!chip) return;
        const y = chip.getAttribute("data-year");
        if (!y) return;

        if (y === "__all") {
          state.activeYears = new Set(state.years);
          renderAll();
          return;
        }

        if (state.activeYears.has(y)) {
          state.activeYears.delete(y);
        } else {
          state.activeYears.add(y);
        }

        if (!state.activeYears.size) {
          state.activeYears = new Set(state.years);
        }

        renderAll();
      });

      for (const btn of document.querySelectorAll(".mode-switch button")) {
        btn.addEventListener("click", () => {
          setView(btn.getAttribute("data-view") || "mosaic");
          renderAll();
        });
      }

      document.getElementById("selectAllVisible").addEventListener("click", () => {
        for (const e of state.filtered) state.selected.add(e.id);
        saveSelection();
        renderAll();
      });

      document.getElementById("clearSelection").addEventListener("click", () => {
        if (!confirm("Merkliste wirklich leeren?")) return;
        state.selected.clear();
        saveSelection();
        renderAll();
      });

      const dlSel = () => {
        const txt = selectionTxt();
        if (!txt) return;
        downloadText("tok_merkliste.txt", txt);
      };

      document.getElementById("downloadSelection").addEventListener("click", dlSel);
      document.getElementById("dockDownload").addEventListener("click", dlSel);
      document.getElementById("heroDownloadList").addEventListener("click", dlSel);

      const openCompare = () => {
        setView("compare");
        renderAll();
      };

      document.getElementById("heroCompare").addEventListener("click", openCompare);
      document.getElementById("dockCompare").addEventListener("click", openCompare);

      document.getElementById("dockClear").addEventListener("click", () => {
        if (!confirm("Merkliste wirklich leeren?")) return;
        state.selected.clear();
        saveSelection();
        renderAll();
      });

      document.getElementById("copySelectionIds").addEventListener("click", copySelectionIds);
      document.getElementById("heroShare").addEventListener("click", copyShareLink);

      document.getElementById("fieldZoomIn").addEventListener("click", () => {
        state.fieldZoom = Math.min(2.4, state.fieldZoom + 0.12);
        applyFieldZoom(true);
      });

      document.getElementById("fieldZoomOut").addEventListener("click", () => {
        state.fieldZoom = Math.max(0.55, state.fieldZoom - 0.12);
        applyFieldZoom(true);
      });

      document.getElementById("fieldZoomReset").addEventListener("click", () => {
        state.fieldZoom = 1;
        applyFieldZoom(true);
      });

      els.fieldZoomRange.addEventListener("input", () => {
        state.fieldZoom = Number(els.fieldZoomRange.value) / 100;
        applyFieldZoom(false);
      });

      els.fieldViewport.addEventListener("wheel", (ev) => {
        if (!ev.altKey) return;
        ev.preventDefault();
        const rect = els.fieldViewport.getBoundingClientRect();
        const ax = ev.clientX - rect.left;
        const ay = ev.clientY - rect.top;
        const delta = ev.deltaY < 0 ? 0.1 : -0.1;
        state.fieldZoom = Math.max(0.55, Math.min(2.4, state.fieldZoom + delta));
        applyFieldZoom(true, ax, ay);
      }, { passive: false });

      els.fieldViewport.addEventListener("pointerdown", (ev) => {
        if (ev.target.closest(".field-node")) return;
        state.fieldDrag = {
          x: ev.clientX,
          y: ev.clientY,
          left: els.fieldViewport.scrollLeft,
          top: els.fieldViewport.scrollTop,
          pointerId: ev.pointerId
        };
        els.fieldViewport.classList.add("dragging");
        els.fieldViewport.setPointerCapture(ev.pointerId);
      });

      els.fieldViewport.addEventListener("pointermove", (ev) => {
        if (!state.fieldDrag || ev.pointerId !== state.fieldDrag.pointerId) return;
        const dx = ev.clientX - state.fieldDrag.x;
        const dy = ev.clientY - state.fieldDrag.y;
        els.fieldViewport.scrollLeft = state.fieldDrag.left - dx;
        els.fieldViewport.scrollTop = state.fieldDrag.top - dy;
      });

      const stopFieldDrag = (ev) => {
        if (!state.fieldDrag || ev.pointerId !== state.fieldDrag.pointerId) return;
        state.fieldDrag = null;
        els.fieldViewport.classList.remove("dragging");
      };

      els.fieldViewport.addEventListener("pointerup", stopFieldDrag);
      els.fieldViewport.addEventListener("pointercancel", stopFieldDrag);
      els.fieldViewport.addEventListener("pointerleave", stopFieldDrag);

      els.compareZoomRange.addEventListener("input", () => {
        state.compareZoom = Number(els.compareZoomRange.value) / 100;
        els.compareZoomLabel.textContent = `${Math.round(state.compareZoom * 100)}%`;
        renderCompare();
      });

      els.compareSyncBtn.addEventListener("click", () => {
        state.compareSync = !state.compareSync;
        els.compareSyncBtn.textContent = `Sync-Pan: ${state.compareSync ? "aktiv" : "aus"}`;
      });

      els.detailClose.addEventListener("click", closeDetail);
      els.detailToggle.addEventListener("click", () => {
        const id = els.detailToggle.getAttribute("data-id") || state.detailId;
        if (!id) return;
        toggleSelected(id);
      });

      els.detailPrev.addEventListener("click", () => {
        const id = els.detailPrev.getAttribute("data-id");
        if (id) openDetail(id);
      });

      els.detailNext.addEventListener("click", () => {
        const id = els.detailNext.getAttribute("data-id");
        if (id) openDetail(id);
      });

      document.addEventListener("keydown", (ev) => {
        if (ev.key === "Escape") closeDetail();
        if (!els.detailPane.classList.contains("open")) return;
        if (ev.key === "ArrowLeft" && !els.detailPrev.disabled) {
          const id = els.detailPrev.getAttribute("data-id");
          if (id) openDetail(id);
        }
        if (ev.key === "ArrowRight" && !els.detailNext.disabled) {
          const id = els.detailNext.getAttribute("data-id");
          if (id) openDetail(id);
        }
      });
    }

    function init() {
      state.entries = RAW_ENTRIES.slice();
      state.years = Array.from(new Set(state.entries.map(e => e.year))).sort((a, b) => Number(a) - Number(b));
      state.activeYears = new Set(state.years);
      state.selected = loadSelection();
      preloadSelectionFromURL();

      els.metaTotal.textContent = String(state.entries.length);
      els.compareZoomLabel.textContent = `${Math.round(state.compareZoom * 100)}%`;
      els.fieldZoomOutLabel.textContent = `${Math.round(state.fieldZoom * 100)}%`;

      setupControls();
      setView(state.view);
      renderAll();
    }

    init();
  </script>
</body>
</html>
'''

    return (
        template
        .replace("__RAW_ENTRIES__", raw_json)
        .replace("__GENERATED_AT__", generated_at)
    )


def main():
    repo_root = Path(__file__).resolve().parents[1]
    csv_path = repo_root / "ausgabe_zeichnungen" / "alle_jahrgaenge" / "total_verzeichnis.csv"
    out_path = repo_root / "ausgabe_zeichnungen" / "alle_jahrgaenge" / "galerie_tok.html"

    entries = load_entries(csv_path)
    html = build_html(entries)
    out_path.write_text(html, encoding="utf-8")

    print(f"Entries: {len(entries)}")
    print(f"Output: {out_path}")


if __name__ == "__main__":
    main()
