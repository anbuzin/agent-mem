CREATE MIGRATION m1eigvfjc74hltziwhjkengvev7jlqjuiidtllan26cdtexq3w4kcq
    ONTO m13x2hixklu6ci7il6qtmzrepnd4iopz5z3wul6pf5gaep65vzvlqq
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
              (.created_at <= cutoff)
          )
      ,
      messages_body := 
          (SELECT
              messages.body
          ORDER BY
              messages.created_at ASC
          )
  SELECT
      std::net::http::schedule_request('http://127.0.0.1:8000/summarize', method := std::net::http::Method.POST, headers := [('Content-Type', 'application/json')], body := std::to_bytes(std::to_str(std::json_object_pack({('chat_id', <std::json>chat_id), ('messages', <std::json>messages_body), ('cutoff', <std::json><std::str>cutoff)}))))
  );
};
