CREATE MIGRATION m14mgwuc64ylf3xkdnojsadx5gpbhe3u3i2kxhy6tew3qs2p4yx6la
    ONTO m1zrqreevtgjhomlzigeggus7acxgz4xgku34wvotwminxbz55fhzq
{
  ALTER TYPE default::Chat {
      DROP TRIGGER summarize;
  };
  DROP GLOBAL default::summary_threshold;
  CREATE GLOBAL default::summary_threshold -> std::int64 {
      SET default := 3;
  };
  ALTER TYPE default::Chat {
      CREATE TRIGGER summarize
          AFTER UPDATE, INSERT 
          FOR EACH DO (SELECT
              (default::request_summary(__new__.id, std::datetime_current()) IF (std::count(__new__.history) > GLOBAL default::summary_threshold) ELSE {})
          );
  };
};
