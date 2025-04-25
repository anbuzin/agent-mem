CREATE MIGRATION m13x2hixklu6ci7il6qtmzrepnd4iopz5z3wul6pf5gaep65vzvlqq
    ONTO m13xvd44kco3b4ufqbunxjma6grlttbqut5gyuawax2pinrng6pxmq
{
  ALTER TYPE default::Message {
      CREATE PROPERTY is_evicted: std::bool {
          SET default := false;
      };
  };
  ALTER FUNCTION default::insert_summary(chat_id: std::uuid, summary: std::str, cutoff: std::datetime) USING (WITH
      chat := 
          std::assert_exists((SELECT
              default::Chat
          FILTER
              (.id = chat_id)
          ))
      ,
      evicted_messages := 
          (UPDATE
              chat.archive
          FILTER
              (.created_at <= cutoff)
          SET {
              is_evicted := true
          })
      ,
      summary_message := 
          (INSERT
              default::Message
              {
                  llm_role := 'system',
                  body := summary,
                  created_at := cutoff
              })
  UPDATE
      chat
  SET {
      archive := DISTINCT ((.archive UNION summary_message))
  });
  ALTER TYPE default::Chat {
      ALTER LINK history {
          USING (SELECT
              .archive
          FILTER
              NOT (.is_evicted)
          );
      };
  };
  CREATE FUNCTION default::request_summary(chat_id: std::uuid, cutoff: std::datetime) ->  std::net::http::ScheduledRequest USING (WITH
      chat := 
          std::assert_exists((SELECT
              default::Chat
          FILTER
              (.id = chat_id)
          ))
      ,
      messages := 
          (SELECT
              chat.history
          FILTER
              (.created_at <= cutoff)
          )
  SELECT
      std::net::http::schedule_request('http://127.0.0.1:8000/structurize', method := std::net::http::Method.POST, headers := [('Content-Type', 'application/json')], body := std::to_bytes(std::to_str(std::json_object_pack({('messages', <std::json>messages), ('cutoff', <std::json>cutoff)}))))
  );
};
