CREATE MIGRATION m1zrqreevtgjhomlzigeggus7acxgz4xgku34wvotwminxbz55fhzq
    ONTO m1yiyar5zvgtz45fkmpctegc646ml4v4ofzkgehbkzyu23wyfspuia
{
  CREATE GLOBAL default::summary_threshold := (3);
  ALTER TYPE default::Chat {
      CREATE TRIGGER summarize
          AFTER UPDATE, INSERT 
          FOR EACH DO (SELECT
              (default::request_summary(__new__.id, std::datetime_current()) IF (std::count(__new__.history) > GLOBAL default::summary_threshold) ELSE {})
          );
  };
};
