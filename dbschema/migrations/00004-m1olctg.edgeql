CREATE MIGRATION m1olctg6yfgiyqhs3bpgckuyrwvm4ybswcc323g34jqbuw4vyqiqya
    ONTO m1e3bijurgw5lxlx7lq7mzgijfo4nlulbvyz4lvuccwiqxyr4njmfa
{
  ALTER TYPE default::Chat {
      ALTER LINK history {
          CREATE REWRITE
              UPDATE 
              USING (SELECT
                  default::History
              );
      };
      DROP TRIGGER summarize;
  };
};
