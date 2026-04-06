# AIS Vessel Tracking

## Problem Statement

Currently, publicly available vessel tracking data is unwieldy and difficult to get insights from. Available options include:
1. Joining the AIS network (requires purchase/operation of expensive equipment)
2. Filing Freedom-of-Information-Act requests with the US Coast Guard
3. Streaming raw data from a WebSocket (not user-friendly or useful for analytics)

However, this data has a lot of valuable applications, including logistics, early market warnings, and national security.

To that end, we aim to create a big-data pipeline that reads the available AIS feed into a data warehouse. We will design an API layer that provides useful methods for accessing the data. Finally, we will provide a sample application for the data, including sophisticated agent for answering questions using the APIs we create + additional third-party integrations.


## System Architecture
```mermaid
architecture-beta
    group api[Ingestion]

    service ais(internet)[AISStream] in api
    service sock(server)[Python websockets] in api
    service db(database)[Snowflake] in api

    service server(server)[Python FastAPI]

    ais:R --> L:sock
    sock:R --> L:db
    db:R --> L:server

    group mcp[MCP]

    service maps(cloud)[Google Maps] in mcp
    service weather(cloud)[OpenWeather] in mcp
    service news(cloud)[GDELT] in mcp
    service ais_wrapper(cloud)[Vessel Locations] in mcp

    service agent(server)[LangGraph]

    maps:R -- L:news
    news:R -- L:weather
    weather:R -- L:ais_wrapper
    ais_wrapper{group}:R --> L:agent

    server:T --> B:ais_wrapper{group}

    service frontend(server)[Streamlit]

    agent:B --> T:frontend
    server:R --> L:frontend
```

## Data Sources

| Source | What Data? | How to Access? | Why We Need It? | What It Returns? | Limitations |
|--------|-----------|----------------|-----------------|------------------|-------------|
| **[AISStream](https://aisstream.io)** (Real-time stream, Free, API key required) | Ship positions, speed, heading, identity, type, dimensions — broadcast by every commercial vessel globally | WebSocket connection using Python `websockets` library. Data is ingested into Snowflake via Snowpipes. Served to users through FastAPI endpoints. | Core data source. Answers "where are ships?" and "how are they moving?" | MMSI, IMO, ship name, lat/lon, speed, course, heading, rate of turn, nav status, ship type, dimensions. ~6,000 messages/min globally. | Coverage gaps. High velocity requires robust pipeline. |
| **[GDELT](https://blog.gdeltproject.org/gdelt-geo-2-0-api-debuts/)** (On-demand API, Free, No key needed) | Global news articles — titles, sources, dates, countries, tone scores, locations. Monitors 100+ languages, updates every 15 minutes. | REST API or Python `gdeltdoc` library. Pass keyword + date range, get back matching articles. No authentication needed. | Provides the "why." If AIS shows traffic dropped, GDELT explains the cause — conflict, sanctions, port strike, disaster. | URL, title, date, domain, language, source country, tone. Up to 250 articles per query. Covers last 3 months (DOC API) or 7 days (GEO API). | English-language bias. Noisy results. Geocoding errors in article tagging. 15-min delay. Rate limiting. |
| **[OpenWeatherMap](https://openweathermap.org/api)** (On-demand API, Free tier, API key required) | Weather conditions at any lat/lon — temperature, wind, humidity, visibility, pressure, cloud cover, weather description. | REST API with API key. Pass lat + lon, get JSON back. Free tier: 1,000 calls/day on v3.0. | Allows agent to inspect historical weather conditions. | Temperature (°C), feels_like, humidity (%), wind_speed (m/s), wind_deg, visibility (m), pressure (hPa), weather description. | Up to 1000 free calls /day. |
| **[Google Maps](https://mapsplatform.google.com/maps-products/)** (On-demand API, $200 free/month, API key + billing required) | Geocoding — converts place names ("Strait of Hormuz") into lat/lon coordinates and bounding boxes. | REST API with API key. Pass place name, get coordinates. Requires Google Cloud project with billing. | Allows agent to translate questions into queries. | Formatted address, lat, lon, bounding box (NE + SW corners), location type. Bounding boxes are critical for AIS area queries. | Maritime terms may resolve poorly. Open ocean areas fail. Needs billing setup. Some ports return point instead of area. |

## Components

### AIS Tracker
1. Data ingested via websocket from [AISStream](https://aisstream.io)
2. Data is parsed and cleaned, then passed into raw tables
3. Data from raw tables is loaded to dimensional model using Snowpipes
4. Data in Snowflake is provided to end applications via FastAPI

#### Dimensional model
```mermaid
erDiagram
    fact_location {
        int location_report_id PK
        datetime timestamp
        geography position
        number rate_of_turn "degrees per minute"
        number speed_over_ground "knots"
        number course_over_ground "degrees (clockwise from north)"
        number true_heading "degrees (clockwise from north)"
        boolean high_accuracy "<=10m"
        int vessel_id FK "surrogate key: mmsi + imo"
        int status_id FK
    }
    dim_vessel {
        int vessel_id PK
        int mmsi
        int imo
        varchar callsign
        varchar vessel_name
        number bow_m
        number stern_m
        number port_m
        number starboard_m
        datetime start_dt
        datetime end_dt
        boolean active
        int vessel_type_id FK
    }

    dim_vessel_type {
        int vessel_type_id
        number source_first_digit
        number source_second_digit
        varchar vessel_category
        varchar vessel_activity
    }
    dim_status {
        int status_id
        int source_status_code
        varchar description
    }
    dim_vessel_type ||--o{ dim_vessel : "vessel_type_id"
    dim_status ||--o{ fact_location : "status_id"
    dim_vessel ||--o{ fact_location : "vessel_id"
```

#### API endpoints

- **/vessels**
    - List all vessels, filtering by vessel characteristics or time/place spotted
- **/vessels/{mmsi}**
    - Get details for a specific vessel using its MMSI (source key)
- **/vessels/{mmsi}/logs**
    - Get list of all position reports published by a vessel in a specified timeframe
    - Can be used for trajectory analysis or plotting

### MCP Server

Wraps services:
- AIS Tracker (above)
- [OpenWeatherMap](https://openweathermap.org/api/one-call-3?collection=one_call_api_3.0)
    - Allows querying weather at a specific location at a specific time (including limited forecasting)
    - Tools:
        - get_weather(lat, lon, timestamp) *Weather report for a specific time*
        - get_day_weather(lat, lon, date) *Aggregate weather report for a specific day*
- [GDELT](https://blog.gdeltproject.org/gdelt-geo-2-0-api-debuts/)
    - Provides powerful querying of international news sources to find events by location/time/keyword.
    - Tools:
        - get_events(query, lat, lon, timestamp)
- [Google Maps](https://mapsplatform.google.com/maps-products/)
    - Allows resolution of natural-language place names to geographic coordinates
    - Tools:
        - search_place(name) *List possible entity resolutions for a natural-language place description (with optional filters)*

These are provided for use in agentic workflows to answer questions such as:

> How has the Iran conflict affected traffic around the Strait of Hormuz?

> How does the number of ships harbored in Sydney Harbor compare to 2 years ago?

> How long did it take ship 219032032 to pass through the Panama Canal on Wednesday?

### Streamlit

**Components:**
1. Interactive map
2. Vessel detail pages
3. Agentic chat

### Work distribution

- Seamus - Ingestion pipeline & FastAPI backend
- Deep -
- Tapan -
