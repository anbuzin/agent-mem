CREATE MIGRATION m1uz7ahh73rbvdoj4lwcsk56dbcraf5f6mov4e5lolslrpdu2q2xhq
    ONTO m14mgwuc64ylf3xkdnojsadx5gpbhe3u3i2kxhy6tew3qs2p4yx6la
{
  ALTER TYPE default::Chat {
      ALTER TRIGGER summarize USING (WITH
          cutoff_messages := 
              (SELECT
                  __new__.history ORDER BY
                      .created_at DESC
              LIMIT
                  GLOBAL default::summary_threshold
              )
          ,
          cutoff := 
              ((SELECT
                  cutoff_messages 
              LIMIT
                  1
              )).created_at
      SELECT
          (default::request_summary(__new__.id, std::assert_exists(cutoff)) IF (std::count(__new__.history) > GLOBAL default::summary_threshold) ELSE {})
      );
  };
};
