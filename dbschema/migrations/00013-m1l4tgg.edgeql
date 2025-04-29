CREATE MIGRATION m1l4tggjvji2ulbbdvjitsjxj5463phli23s5di4aqxywugpbdtrna
    ONTO m1zxp2i77rnjpeai43eczd466esfxzgirle4jfulz4j4a4tymg2ixa
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
          std::array_agg((SELECT
              chat.history
          FILTER
              (.created_at <= cutoff)
          ))
  SELECT
      std::net::http::schedule_request('http://127.0.0.1:8000/summarize', method := std::net::http::Method.POST, headers := [('Content-Type', 'application/json')], body := std::to_bytes(std::to_str(std::json_object_pack({('chat_id', <std::json>chat_id), ('messages', <std::json>messages), ('cutoff', <std::json>cutoff)}))))
  );
};
