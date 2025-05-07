CREATE MIGRATION m16jnrcfkru6iuimrv7uk7h6cv4tidyk7qros3r4llaag4hwzes4ha
    ONTO m1ljqptjmegd5q3afkj4cu2wgxc5qacsdbp6llotzbube46jomvdva
{
  ALTER TYPE default::Chat {
      CREATE TRIGGER get_title
          AFTER UPDATE 
          FOR EACH DO (WITH
              messages := 
                  (SELECT
                      __new__.history
                  ORDER BY
                      .created_at ASC
                  )
              ,
              messages_body := 
                  std::array_agg((SELECT
                      messages.body
                  ORDER BY
                      messages.created_at ASC
                  ))
          SELECT
              (std::net::http::schedule_request('http://127.0.0.1:8000/get_title', method := std::net::http::Method.POST, headers := [('Content-Type', 'application/json')], body := std::to_bytes(std::to_str(std::json_object_pack({('chat_id', <std::json>__new__.id), ('messages', <std::json>messages_body)})))) IF NOT (EXISTS (__new__.title)) ELSE {})
          );
  };
};
