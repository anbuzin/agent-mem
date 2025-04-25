CREATE MIGRATION m13xvd44kco3b4ufqbunxjma6grlttbqut5gyuawax2pinrng6pxmq
    ONTO m17zhfknonskygbv3fsgo7qs7ficwbk53yhl5hcztxvmbs53v6btvq
{
  ALTER TYPE default::Chat {
      DROP LINK history;
      CREATE MULTI LINK history: default::Message;
  };
  CREATE FUNCTION default::insert_summary(chat_id: std::uuid, summary: std::str, cutoff: std::datetime) ->  default::Chat USING (WITH
      chat := 
          std::assert_exists((SELECT
              default::Chat
          FILTER
              (.id = chat_id)
          ))
      ,
      remaining_messages := 
          (SELECT
              chat.history
          FILTER
              (.created_at > cutoff)
          )
      ,
      summary_message := 
          (INSERT
              default::Message
              {
                  llm_role := 'system',
                  body := summary,
                  created_at := cutoff
              })
      ,
      new_history := 
          (summary_message UNION remaining_messages)
  UPDATE
      chat
  SET {
      history := new_history
  });
  DROP TYPE default::History;
};
