CREATE TABLE IF NOT EXISTS stocks (
  ticker        TEXT          PRIMARY KEY,
  index         TEXT          NOT NULL,
  source        TEXT          NOT NULL,
  yahoo_ticker  TEXT          NOT NULL,
  company_name  TEXT          NOT NULL,
  date_added    TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS daily (
  date              TIMESTAMPTZ       NOT NULL,
  ticker            TEXT              NOT NULL,
  high_price        DOUBLE PRECISION  NULL,
  low_price         DOUBLE PRECISION  NULL,
  open_price        DOUBLE PRECISION  NULL,
  close_price       DOUBLE PRECISION  NULL,
  volume            BIGINT            NULL,
  adj_close_price   DOUBLE PRECISION  NULL,
  UNIQUE (date, ticker)
);

SELECT create_hypertable('daily', 'date');
