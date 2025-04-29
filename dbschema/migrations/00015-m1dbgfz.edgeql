CREATE MIGRATION m1dbgfzt2vmehzylpglgiaolfpfhqentwbage4kjeaguxukjkzs7qa
    ONTO m1nzsercsmt7h5nwaobjof4ogu3b35p2b2rxp7envwaohkduyen3nq
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
              chat.history {
                  llm_role,
                  body,
                  created_at
              }
          FILTER
              (.created_at <= cutoff)
          )
      ,
      messages_body := 
          std::array_agg((SELECT
              messages.body
          ORDER BY
              messages.created_at ASC
          ))
  SELECT
      std::net::http::schedule_request('http://127.0.0.1:8000/summarize', method := std::net::http::Method.POST, headers := [('Content-Type', 'application/json')], body := std::to_bytes(std::to_str(std::json_object_pack({('chat_id', <std::json>chat_id), ('messages', <std::json>messages), ('cutoff', <std::json>cutoff)}))))
  );
};
