CREATE MIGRATION m17zhfknonskygbv3fsgo7qs7ficwbk53yhl5hcztxvmbs53v6btvq
    ONTO m1qeidletnql3zwtm2rsz53bcmr5pepczawdfvssq5hq53lufploqa
{
  ALTER TYPE default::Chat {
      ALTER LINK history {
          DROP REWRITE
              UPDATE ;
          };
      };
  ALTER TYPE default::Chat {
      ALTER LINK history {
          CREATE REWRITE
              UPDATE 
              USING (WITH
                  history := 
                      (SELECT
                          default::History
                      FILTER
                          (.id = __subject__.history.id)
                      )
              SELECT
                  (INSERT
                      default::History
                  )
              );
      };
  };
};
