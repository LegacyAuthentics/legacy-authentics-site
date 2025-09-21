#!/usr/bin/env python3
"""
authenticon_seed.py

Seed generator for an autograph authentication system.

Features
- Generates N unique 6-digit serial numbers (no leading zeros stripped).
- Attaches a role, celebrity name, and item description.
- Deterministic runs via --seed (or AUTHENTICON_SEED env var).
- Validates uniqueness and serial format.
- Writes JSON or CSV. Also usable as a library.

CLI
  python authenticon_seed.py --count 250 --out data.json --format json --seed 42
  python authenticon_seed.py --count 200 --out data.csv  --format csv

Library
  from authenticon_seed import generate_dataset
  records = generate_dataset(count=300, seed=123)
"""
from __future__ import annotations
import argparse
import csv
import json
import os
import random
import re
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Iterable, List, Set

SERIAL_RE = re.compile(r"^\d{6}$")

# --- Domain model ------------------------------------------------------------

@dataclass(frozen=True)
class AuthRecord:
    serial_number: str          # 6 digits, zero-padded if needed
    role: str                   # e.g., "Athlete", "Singer", "Actor", ...
    celebrity: str              # e.g., "LeBron James"
    item_description: str       # e.g., "2006 Cleveland Cavaliers jersey"
    year: int                   # provenance hint
    source: str                 # "seed-generator v1"

# --- Catalogs (tweak/extend freely) -----------------------------------------

ROLES = [
    "Athlete", "Singer", "Actor", "Comedian", "Director",
    "Influencer", "Author", "DJ", "Producer", "Esports Athlete"
]

CELEBS = {
    "Athlete": [
        "LeBron James", "Michael Jordan", "Kobe Bryant", "Tom Brady", "Serena Williams",
        "Lionel Messi", "Cristiano Ronaldo", "Stephen Curry", "Shohei Ohtani", "Usain Bolt",
        "Simone Biles", "Kevin Durant", "Derek Jeter", "Mike Tyson", "Roger Federer",
        "Novak Djokovic", "Rafael Nadal", "Patrick Mahomes", "Wayne Gretzky", "Megan Rapinoe",
    ],
    "Singer": [
        "Taylor Swift", "Beyoncé", "Rihanna", "Adele", "Ed Sheeran",
        "Billie Eilish", "Bruno Mars", "The Weeknd", "Drake", "Harry Styles",
        "Dua Lipa", "Post Malone", "Olivia Rodrigo", "Bad Bunny", "Ariana Grande",
        "Kendrick Lamar", "Doja Cat", "SZA", "Travis Scott", "Justin Bieber",
    ],
    "Actor": [
        "Robert Downey Jr.", "Scarlett Johansson", "Keanu Reeves", "Jennifer Lawrence",
        "Denzel Washington", "Leonardo DiCaprio", "Tom Hanks", "Zendaya", "Ryan Gosling",
        "Margot Robbie", "Chris Hemsworth", "Emma Stone", "Pedro Pascal", "Sydney Sweeney",
        "Cillian Murphy", "Emily Blunt", "Ana de Armas", "Jason Momoa", "Paul Rudd", "Brie Larson",
    ],
    "Comedian": [
        "Dave Chappelle", "Kevin Hart", "John Mulaney", "Ali Wong", "Trevor Noah",
        "Hasan Minhaj", "Ricky Gervais", "Tiffany Haddish", "Bo Burnham", "Nate Bargatze",
    ],
    "Director": [
        "Christopher Nolan", "Greta Gerwig", "Quentin Tarantino", "Jordan Peele",
        "Denis Villeneuve", "Martin Scorsese", "Patty Jenkins", "Taika Waititi",
        "Ryan Coogler", "Guillermo del Toro",
    ],
    "Influencer": [
        "MrBeast", "Charli D'Amelio", "Ninja", "Mark Rober", "Emma Chamberlain",
        "KSI", "Logan Paul", "Lilly Singh", "PewDiePie", "Marques Brownlee",
    ],
    "Author": [
        "Stephen King", "Neil Gaiman", "Margaret Atwood", "Colleen Hoover", "George R.R. Martin",
        "Brandon Sanderson", "Malcolm Gladwell", "Michelle Obama", "James Patterson", "Rick Riordan",
    ],
    "DJ": [
        "Calvin Harris", "Skrillex", "Deadmau5", "David Guetta", "Marshmello",
        "Zedd", "Armin van Buuren", "Diplo", "Kygo", "Alesso",
    ],
    "Producer": [
        "Pharrell Williams", "Rick Rubin", "Dr. Dre", "Metro Boomin", "Timbaland",
        "Mark Ronson", "Mike Will Made-It", "Finneas O'Connell", "Jack Antonoff", "Max Martin",
    ],
    "Esports Athlete": [
        "Faker", "s1mple", "N0tail", "TenZ", "Bugha", "Ninja", "Magisk", "MONESY", "ZywOo", "Caps",
    ],
}

ITEM_TEMPLATES = {
    "Athlete": [
        "{year} {team} jersey",
        "Game-used {sport} ball",
        "{event} ticket stub",
        "{team} warmup jacket",
        "Replica championship ring box",
        "{year} All-Star cap",
        "Limited poster: {event}",
        "Custom photo: {year} season",
        "Mini-helmet {team}",
        "Signed cleat {year}"
    ],
    "Singer": [
        "{album} vinyl",
        "{tour} tour poster",
        "Concert setlist {year}",
        "Microphone windscreen",
        "Acoustic guitar pickguard",
        "Tour hoodie {year}",
        "Lyric sheet facsimile",
        "Backstage pass {tour}",
        "CD booklet {album}",
        "Promo photo {year}"
    ],
    "Actor": [
        "{film} movie poster",
        "{film} script cover",
        "Blu-ray slipcover {film}",
        "Premiere ticket {year}",
        "Character photo still ({film})",
        "Prop replica ({prop})",
        "Press kit one-sheet",
        "Lobby card ({film})",
        "Director’s chair back ({film})",
        "Clapperboard plate ({film})"
    ],
    "Comedian": [
        "{tour} tour poster",
        "Show flyer {venue} ({year})",
        "Mic flag cube",
        "Netflix special card ({special})",
        "Green room pass {year}",
        "Promo 8x10 headshot",
        "Ticket stub {venue}",
        "Merch tee ({tour})",
        "Set list card ({year})",
        "Stool-top coaster ({venue})"
    ],
    "Director": [
        "{film} call sheet (facsimile)",
        "Storyboard card ({film})",
        "Festival pass ({year})",
        "Slate label ({film})",
        "Press screening ticket",
        "One-sheet ({film})",
        "Location pass ({film})",
        "Q&A card ({year})",
        "Premiere program ({film})",
        "Draft cover page ({film})"
    ],
    "Influencer": [
        "Meet & greet badge ({year})",
        "Channel banner print",
        "Merch hoodie drop ({year})",
        "Creator Games pass",
        "Thumbnail board ({series})",
        "Signed Polaroid ({year})",
        "Sticker sheet ({series})",
        "Camera skin ({year})",
        "Creator card ({platform})",
        "Challenge poster ({series})"
    ],
    "Author": [
        "{book} hardcover dust jacket",
        "ARC cover ({book})",
        "Bookplate ({year})",
        "Tour stop flyer ({year})",
        "Bookmark ({book})",
        "Reading pass ({venue})",
        "Book club card ({book})",
        "Signing ticket ({venue})",
        "Promo postcard ({book})",
        "Manuscript title page ({book})"
    ],
    "DJ": [
        "Festival wristband ({year})",
        "Setlist card ({festival})",
        "Slipmat ({year})",
        "USB shell ({year})",
        "Backstage pass ({festival})",
        "Tour poster ({tour})",
        "Headphone case plate",
        "Promo one-sheet ({year})",
        "Lanyard tag ({festival})",
        "Flyer ({club})"
    ],
    "Producer": [
        "Studio track sheet ({year})",
        "808 faceplate ({year})",
        "Session notes card",
        "Plat plaque card ({album})",
        "Console strip ({year})",
        "Merch tee ({year})",
        "Vinyl jacket ({album})",
        "Press card ({album})",
        "Patch bay label",
        "Promo postcard ({album})"
    ],
    "Esports Athlete": [
        "{org} jersey ({year})",
        "Stage pass ({event})",
        "Mousepad ({year})",
        "Team flag ({org})",
        "LAN badge ({event})",
        "Poster ({event})",
        "Keyboard frame ({year})",
        "Player card ({event})",
        "Coach board ({org})",
        "Scrim sheet ({year})"
    ],
}

SPORT_BY_ATHLETE = {
    "LeBron James": ("basketball", "Cleveland Cavaliers"),
    "Michael Jordan": ("basketball", "Chicago Bulls"),
    "Kobe Bryant": ("basketball", "Los Angeles Lakers"),
    "Tom Brady": ("football", "New England Patriots"),
    "Serena Williams": ("tennis", "USA"),
    "Lionel Messi": ("soccer", "Argentina"),
    "Cristiano Ronaldo": ("soccer", "Portugal"),
    "Stephen Curry": ("basketball", "Golden State Warriors"),
    "Shohei Ohtani": ("baseball", "Los Angeles Dodgers"),
    "Usain Bolt": ("track", "Jamaica"),
    "Simone Biles": ("gymnastics", "USA"),
    "Kevin Durant": ("basketball", "Phoenix Suns"),
    "Derek Jeter": ("baseball", "New York Yankees"),
    "Mike Tyson": ("boxing", "USA"),
    "Roger Federer": ("tennis", "Switzerland"),
    "Novak Djokovic": ("tennis", "Serbia"),
    "Rafael Nadal": ("tennis", "Spain"),
    "Patrick Mahomes": ("football", "Kansas City Chiefs"),
    "Wayne Gretzky": ("hockey", "Edmonton Oilers"),
    "Megan Rapinoe": ("soccer", "USA"),
}

# --- Helpers ----------------------------------------------------------------

def _pick_year(rng: random.Random) -> int:
    # Prefer modern memorabilia, lightly biased to recent years.
    base = rng.randint(2004, datetime.now().year)
    # small nudge towards later years
    return max(base, rng.randint(2012, datetime.now().year))

def _six_digit_unique(rng: random.Random, used: Set[str]) -> str:
    # Generate a truly 6-digit numeric code (000000–999999 allowed? Spec says 6-digit serial; usually avoid leading 0s.)
    # We'll enforce 6 digits, first digit 1–9 to avoid leading zero confusion.
    while True:
        s = f"{rng.randint(100000, 999999)}"
        if s not in used:
            used.add(s)
            return s

def _format_item(rng: random.Random, role: str, celeb: str, year: int) -> str:
    tmpl = rng.choice(ITEM_TEMPLATES[role])
    # Lightweight vocab pools
    albums = ["1989", "Lemonade", "21", "After Hours", "Take Care", "Folklore", "Scorpion", "Starboy", "Sour", "UTOPIA"]
    tours  = ["Eras", "Formation", "Monsters of Pop", "World Tour", "Summer Stadiums", "Neon Nights", "Happier Than Ever"]
    events = ["Wimbledon Final", "NBA Finals", "Super Bowl", "World Cup Final", "US Open", "Champions League Final"]
    films  = ["Oppenheimer", "Dune", "Barbie", "Titanic", "The Matrix", "Pulp Fiction", "Avengers: Endgame", "John Wick"]
    props  = ["helmet", "shield", "gauntlet", "ring", "badge", "watch"]
    venues = ["Madison Square Garden", "The Forum", "O2 Arena", "Comedy Cellar", "Laugh Factory"]
    specials = ["Paper Tiger", "Tamborine", "Sticks & Stones", "Baby Cobra", "Homecoming"]
    series = ["Challenge Series", "24 Hours", "Tech Reviews", "Creator Games", "Daily Vlog"]
    platforms = ["YouTube", "Twitch", "TikTok", "Instagram"]
    book_titles = ["The Long Night", "Ocean of Stars", "Electric Dreams", "Paper Hearts", "Hidden Doors"]
    festivals = ["Coachella", "Ultra", "Tomorrowland", "EDC", "Lollapalooza"]
    clubs = ["Ministry of Sound", "Fabric", "Pacha", "Berghain", "Output"]
    orgs = ["T1", "G2 Esports", "Fnatic", "Team Liquid", "Cloud9"]
    esports_events = ["Worlds", "IEM Katowice", "The International", "Valorant Masters", "ESL One"]
    teams = ["Chicago Bulls", "Los Angeles Lakers", "New England Patriots", "Golden State Warriors", "New York Yankees"]

    # Role-aware fill-ins
    mapping = {
        "year": year,
        "album": rng.choice(albums),
        "tour": rng.choice(tours),
        "event": rng.choice(events),
        "film": rng.choice(films),
        "prop": rng.choice(props),
        "venue": rng.choice(venues),
        "special": rng.choice(specials),
        "series": rng.choice(series),
        "platform": rng.choice(platforms),
        "book": rng.choice(book_titles),
        "festival": rng.choice(festivals),
        "club": rng.choice(clubs),
        "org": rng.choice(orgs),
        "team": rng.choice(teams),
        "sport": "sport",
    }

    if role == "Athlete":
        sport, team = SPORT_BY_ATHLETE.get(celeb, ("sport", rng.choice(teams)))
        mapping["sport"] = sport
        mapping["team"] = team
        # For athletes, prefer event templates sometimes
        if rng.random() < 0.25:
            mapping["event"] = rng.choice(["NBA Finals", "Super Bowl", "World Series", "Wimbledon Final", "US Open"])
    elif role == "Esports Athlete":
        mapping["event"] = rng.choice(esports_events)
        mapping["org"] = rng.choice(orgs)

    return tmpl.format(**mapping)

# --- Public API --------------------------------------------------------------

def generate_dataset(count: int = 200, seed: int | None = None) -> List[AuthRecord]:
    """
    Generate `count` unique AuthRecord rows with valid 6-digit serials.
    """
    if count < 1:
        raise ValueError("count must be >= 1")
    # Seed hierarchy: CLI arg > ENV > None
    if seed is None:
        env_seed = os.getenv("AUTHENTICON_SEED")
        seed = int(env_seed) if env_seed and env_seed.isdigit() else None

    rng = random.Random(seed)
    used: Set[str] = set()
    records: List[AuthRecord] = []

    # Build a flattened (role, celeb) pool to draw from
    role_celeb_pool: List[tuple[str, str]] = []
    for role, names in CELEBS.items():
        for name in names:
            role_celeb_pool.append((role, name))

    # Ensure we can generate arbitrary counts (with repeats of celebs allowed)
    for _ in range(count):
        role, celeb = rng.choice(role_celeb_pool)
        year = _pick_year(rng)
        item = _format_item(rng, role, celeb, year)
        serial = _six_digit_unique(rng, used)
        rec = AuthRecord(
            serial_number=serial,
            role=role,
            celebrity=celeb,
            item_description=item,
            year=year,
            source="seed-generator v1",
        )
        records.append(rec)

    _validate(records)
    return records

def _validate(records: Iterable[AuthRecord]) -> None:
    seen: Set[str] = set()
    for r in records:
        if not SERIAL_RE.match(r.serial_number):
            raise ValueError(f"Invalid serial format: {r.serial_number}")
        if r.serial_number in seen:
            raise ValueError(f"Duplicate serial: {r.serial_number}")
        seen.add(r.serial_number)

# --- Serialization -----------------------------------------------------------

def write_json(records: List[AuthRecord], path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump([asdict(r) for r in records], f, ensure_ascii=False, indent=2)

def write_csv(records: List[AuthRecord], path: str) -> None:
    fields = ["serial_number", "role", "celebrity", "item_description", "year", "source"]
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in records:
            w.writerow(asdict(r))

# --- CLI --------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate autograph authenticon seed data.")
    p.add_argument("--count", type=int, default=200, help="Number of records to generate (default: 200)")
    p.add_argument("--out", type=str, default="authenticon_seed.json", help="Output file path")
    p.add_argument("--format", choices=["json", "csv"], default="json", help="Output format")
    p.add_argument("--seed", type=int, default=None, help="Deterministic RNG seed (overrides AUTHENTICON_SEED)")
    return p.parse_args()

def main() -> None:
    args = _parse_args()
    records = generate_dataset(count=args.count, seed=args.seed)
    if args.format == "json":
        write_json(records, args.out)
    else:
        write_csv(records, args.out)
    print(f"Wrote {len(records)} records to {args.out} ({args.format}).")

if __name__ == "__main__":
    main()
