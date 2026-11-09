"""
METROPULSE — Data Dictionary
Describes each analytical dataset, its source, columns, and units.
"""

DATA_DICTIONARY = {
    "tube_link_loads": {
        "description": (
            "Passenger link loads between consecutive LU stations. "
            "Represents the estimated number of passengers travelling on a "
            "given track section between two stations in a specified direction "
            "during a typical operating day. Source: Link_Loads worksheet."
        ),
        "source_sheet": "Link_Loads",
        "primary_key": ["link", "year", "day_type"],
        "columns": {
            "link":          "Composite link identifier (From_ASC > To_ASC @ Line)",
            "line":          "Line name (e.g. Bakerloo)",
            "line_code":     "Line code (e.g. BAK)",
            "direction":     "Direction (NB/SB/EB/WB/IB/OB)",
            "order":         "Sequential station order along line",
            "from_nlc":      "NLC code of origin station",
            "from_asc":      "ASC code of origin station",
            "from_station":  "Name of origin station",
            "to_nlc":        "NLC code of destination station",
            "to_asc":        "ASC code of destination station",
            "to_station":    "Name of destination station",
            "total":         "Total daily passenger link load",
            "early":         "Passengers in Early period (05:00–06:30)",
            "am_peak":       "Passengers in AM Peak (06:30–09:30)",
            "midday":        "Passengers in Midday (09:30–16:00)",
            "pm_peak":       "Passengers in PM Peak (16:00–19:00)",
            "evening":       "Passengers in Evening (19:00–22:00)",
            "late":          "Passengers in Late period (22:00–close)",
            "year":          "Dataset year (2023, 2024, 2025)",
            "day_type":      "Day type code (MON, TWT, FRI, SAT, SUN)",
            "source_file":   "Source Excel filename",
        },
        "units": "Number of passengers (estimated typical day)",
        "notes": (
            "NUMBAT data represents a modelled typical operating day, not "
            "actual observed counts for a specific date. Passenger loads "
            "between non-adjacent stations should not be summed."
        ),
    },
    "tube_link_frequencies": {
        "description": (
            "Train frequencies (number of trains) on each LU link by time period. "
            "Source: Link_Frequencies worksheet."
        ),
        "source_sheet": "Link_Frequencies",
        "primary_key": ["link", "year", "day_type"],
        "columns": {
            "link":          "Composite link identifier",
            "line":          "Line name",
            "line_code":     "Line code",
            "direction":     "Direction",
            "order":         "Sequential station order",
            "from_nlc":      "NLC code of origin station",
            "from_asc":      "ASC code of origin station",
            "from_station":  "Name of origin station",
            "to_nlc":        "NLC code of destination station",
            "to_asc":        "ASC code of destination station",
            "to_station":    "Name of destination station",
            "total":         "Total trains across the day",
            "early":         "Trains in Early period",
            "am_peak":       "Trains in AM Peak",
            "midday":        "Trains in Midday",
            "pm_peak":       "Trains in PM Peak",
            "evening":       "Trains in Evening",
            "late":          "Trains in Late period",
            "year":          "Dataset year",
            "day_type":      "Day type code",
            "source_file":   "Source Excel filename",
        },
        "units": "Number of trains (scheduled)",
        "notes": "Frequency values may represent scheduled rather than actual operated trains.",
    },
    "tube_line_boarders": {
        "description": (
            "Total boarders (passengers boarding) by LU line and time period. "
            "Source: Line_Boarders worksheet."
        ),
        "source_sheet": "Line_Boarders",
        "primary_key": ["line_code", "year", "day_type"],
        "columns": {
            "mode":       "Transport mode (LU for Underground)",
            "line_code":  "Line code",
            "line_name":  "Line name",
            "total":      "Total boarders across the day",
            "early":      "Boarders in Early period",
            "am_peak":    "Boarders in AM Peak",
            "midday":     "Boarders in Midday",
            "pm_peak":    "Boarders in PM Peak",
            "evening":    "Boarders in Evening",
            "late":       "Boarders in Late period",
            "year":       "Dataset year",
            "day_type":   "Day type code",
            "source_file": "Source Excel filename",
        },
        "units": "Number of passengers boarding",
    },
    "tube_station_entries": {
        "description": (
            "Station-level passenger entries (tap-ins). "
            "Source: Station_Entries worksheet."
        ),
        "source_sheet": "Station_Entries",
        "primary_key": ["nlc", "year", "day_type"],
        "columns": {
            "nlc":        "National Location Code (station numeric ID)",
            "asc":        "Alpha Station Code",
            "station":    "Station name",
            "fare_zone":  "Fare zone(s)",
            "total":      "Total entries across the day",
            "early":      "Entries in Early period",
            "am_peak":    "Entries in AM Peak",
            "midday":     "Entries in Midday",
            "pm_peak":    "Entries in PM Peak",
            "evening":    "Entries in Evening",
            "late":       "Entries in Late period",
            "year":       "Dataset year",
            "day_type":   "Day type code",
            "source_file": "Source Excel filename",
        },
        "units": "Number of passenger entries",
        "notes": "Entries include all modes using the station. LU filtering applied via ASC suffix 'u'.",
    },
    "tube_station_exits": {
        "description": "Station-level passenger exits (tap-outs). Source: Station_Exits.",
        "source_sheet": "Station_Exits",
        "primary_key": ["nlc", "year", "day_type"],
        "columns": {
            "nlc":        "National Location Code",
            "asc":        "Alpha Station Code",
            "station":    "Station name",
            "fare_zone":  "Fare zone(s)",
            "total":      "Total exits across the day",
            "year":       "Dataset year",
            "day_type":   "Day type code",
        },
        "units": "Number of passenger exits",
    },
    "tube_station_boarders": {
        "description": (
            "Platform-level boarders for LU platforms. Contains Mode column "
            "for direct LU filtering. Source: Station_Boarders."
        ),
        "source_sheet": "Station_Boarders",
        "primary_key": ["id", "year", "day_type"],
        "columns": {
            "id":         "Internal row ID",
            "nlc":        "National Location Code",
            "asc":        "Alpha Station Code",
            "station":    "Station name",
            "mode":       "Transport mode",
            "line":       "Line name",
            "line_code":  "Line code",
            "direction":  "Direction (IB/OB or EB/WB/NB/SB)",
            "platform":   "Platform description",
            "total":      "Total boarders",
            "year":       "Dataset year",
            "day_type":   "Day type code",
        },
        "units": "Number of passengers boarding at platform",
    },
    "tube_station_alighters": {
        "description": (
            "Platform-level alighters for LU platforms. Contains Mode column "
            "for direct LU filtering. Source: Station_Alighters."
        ),
        "source_sheet": "Station_Alighters",
        "primary_key": ["id", "year", "day_type"],
        "columns": {
            "id":         "Internal row ID",
            "nlc":        "National Location Code",
            "asc":        "Alpha Station Code",
            "station":    "Station name",
            "mode":       "Transport mode",
            "line":       "Line name",
            "line_code":  "Line code",
            "direction":  "Direction",
            "platform":   "Platform description",
            "total":      "Total alighters",
            "year":       "Dataset year",
            "day_type":   "Day type code",
        },
        "units": "Number of passengers alighting at platform",
    },
    "tube_station_flows": {
        "description": (
            "Station-to-station passenger flow movements within complex stations. "
            "Source: Station_Flows."
        ),
        "source_sheet": "Station_Flows",
        "primary_key": ["id", "year", "day_type"],
        "columns": {
            "id":           "Flow identifier",
            "complex_nlc":  "Complex station NLC",
            "from_nlc":     "Origin NLC",
            "from_asc":     "Origin ASC",
            "from_station": "Origin station name",
            "from_node":    "Origin node description",
            "to_nlc":       "Destination NLC",
            "to_asc":       "Destination ASC",
            "to_station":   "Destination station name",
            "to_node":      "Destination node description",
            "movement":     "Movement type",
            "total":        "Total flow",
            "year":         "Dataset year",
            "day_type":     "Day type code",
        },
        "units": "Number of passenger movements",
    },
}

