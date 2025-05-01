CREATE MIGRATION m1ixstp4rpd7aby66rxd2qzshheuip3d4hf6lgvzutmi5soo3qjvwq
    ONTO m1a7gpnhgpmtrie7oebge2okop3pxggmo3rr2qg7fyenmcvjivb4ra
{
  DROP FUNCTION default::insert_summary(chat_id: std::uuid, summary: std::str, cutoff: std::datetime);
  ALTER FUNCTION default::request_summary(chat_id: std::uuid, cutoff: std::datetime) USING (WITH
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
              (.created_at < cutoff)
          )
      ,
      summary_datetime := 
          (SELECT
              messages.created_at ORDER BY
                  messages.created_at DESC
          LIMIT
              1
          )
      ,
      messages_body := 
          std::array_agg((SELECT
              messages.body
          ORDER BY
              messages.created_at ASC
          ))
  SELECT
      std::net::http::schedule_request('http://127.0.0.1:8000/summarize', method := std::net::http::Method.POST, headers := [('Content-Type', 'application/json')], body := std::to_bytes(std::to_str(std::json_object_pack({('chat_id', <std::json>chat_id), ('messages', <std::json>messages_body), ('cutoff', <std::json>cutoff), ('summary_datetime', <std::json>summary_datetime)}))))
  );
  CREATE FUNCTION default::insert_summary(chat_id: std::uuid, cutoff: std::datetime, summary: std::str, summary_datetime: std::datetime) ->  default::Chat USING (WITH
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
              (.created_at < cutoff)
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
                  created_at := summary_datetime
              })
  UPDATE
      chat
  SET {
      archive := DISTINCT ((.archive UNION summary_message))
  });
};
