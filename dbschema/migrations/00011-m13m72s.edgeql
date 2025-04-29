CREATE MIGRATION m13m72sg7sw4u3wxodra3ux4xuv67c2n7zxqrgs7inlzxe26z42haq
    ONTO m1wyf2i7yazpomun3afeub3mn6jn6m4mparyqwpbbsxmtgpasof33a
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
