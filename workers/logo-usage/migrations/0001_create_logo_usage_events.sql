CREATE TABLE IF NOT EXISTS logo_usage_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  occurred_at TEXT NOT NULL,
  event_date TEXT NOT NULL,
  event_type TEXT NOT NULL,
  path TEXT NOT NULL DEFAULT '',
  referrer_host TEXT NOT NULL DEFAULT '',
  country TEXT NOT NULL DEFAULT '',
  colo TEXT NOT NULL DEFAULT '',
  device TEXT NOT NULL DEFAULT '',
  viewport_width INTEGER NOT NULL DEFAULT 0,
  viewport_height INTEGER NOT NULL DEFAULT 0,
  ui_lang TEXT NOT NULL DEFAULT '',
  org TEXT NOT NULL DEFAULT '',
  category TEXT NOT NULL DEFAULT '',
  layout TEXT NOT NULL DEFAULT '',
  logo_lang TEXT NOT NULL DEFAULT '',
  color_mode TEXT NOT NULL DEFAULT '',
  scale_value REAL NOT NULL DEFAULT 0,
  advanced_open INTEGER NOT NULL DEFAULT 0,
  custom_text_length INTEGER NOT NULL DEFAULT 0,
  export_format TEXT NOT NULL DEFAULT '',
  session_hash TEXT NOT NULL DEFAULT '',
  visitor_day_hash TEXT NOT NULL DEFAULT '',
  cf_ray TEXT NOT NULL DEFAULT ''
);

CREATE INDEX IF NOT EXISTS idx_logo_usage_events_date_type
  ON logo_usage_events (event_date, event_type);

CREATE INDEX IF NOT EXISTS idx_logo_usage_events_export_format
  ON logo_usage_events (event_date, export_format);

CREATE INDEX IF NOT EXISTS idx_logo_usage_events_session
  ON logo_usage_events (event_date, session_hash);

CREATE INDEX IF NOT EXISTS idx_logo_usage_events_visitor_day
  ON logo_usage_events (event_date, visitor_day_hash);
