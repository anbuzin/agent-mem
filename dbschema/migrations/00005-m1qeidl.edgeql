CREATE MIGRATION m1qeidletnql3zwtm2rsz53bcmr5pepczawdfvssq5hq53lufploqa
    ONTO m1olctg6yfgiyqhs3bpgckuyrwvm4ybswcc323g34jqbuw4vyqiqya
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
                  std::assert_single(history)
              );
      };
  };
};
