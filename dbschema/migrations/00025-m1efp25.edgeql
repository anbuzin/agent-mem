CREATE MIGRATION m1efp252n5tuvzdro4f5uukfx2cc4dgrdvx2sc2mvw6u7gaz7yl76a
    ONTO m1wjrotx4zdy7qddie5vhjhjhxqhbbmvqhfwz3oc7ruszidiygcdla
{
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
      messages_body := 
          std::array_agg((SELECT
              messages.body
          ORDER BY
              messages.created_at ASC
          ))
  SELECT
      std::net::http::schedule_request('http://127.0.0.1:8000/summarize', method := std::net::http::Method.POST, headers := [('Content-Type', 'application/json')], body := std::to_bytes(std::to_str(std::json_object_pack({('chat_id', <std::json>chat_id), ('messages', <std::json>messages_body), ('cutoff', <std::json>cutoff)}))))
  );
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
                  created_at := cutoff
              })
  UPDATE
      chat
  SET {
      archive := DISTINCT ((.archive UNION summary_message))
  });
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
          last_message := 
              (SELECT
                  remaining_messages ORDER BY
                      .created_at DESC
              LIMIT
                  1
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
          (default::request_summary(__new__.id, std::assert_exists(cutoff_message.created_at)) IF ((std::count(__new__.history) > GLOBAL default::summary_threshold) AND (last_message.llm_role = 'assistant')) ELSE {})
      );
  };
};
