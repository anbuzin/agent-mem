CREATE MIGRATION m1wjrotx4zdy7qddie5vhjhjhxqhbbmvqhfwz3oc7ruszidiygcdla
    ONTO m13soi3rov5qejjcnbnkl3wxpl6xsqibihc6d2i4s725wad2vf5z3q
{
  ALTER TYPE default::Chat {
      ALTER TRIGGER summarize USING (WITH
          remaining_messages := 
              (SELECT
                  __new__.history ORDER BY
                      .created_at DESC
              LIMIT
                  GLOBAL default::num_messages_to_leave
              )
          ,
          cutoff_message := 
              (SELECT
                  remaining_messages ORDER BY
                      .created_at ASC
              LIMIT
                  1
              )
      SELECT
          (default::request_summary(__new__.id, std::assert_exists(cutoff_message.created_at)) IF ((std::count(__new__.history) > GLOBAL default::summary_threshold) AND (cutoff_message.llm_role = 'assistant')) ELSE {})
      );
  };
};
