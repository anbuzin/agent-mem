CREATE MIGRATION m1bjegcy6dmkrjjphttryegympsnncxmatrnzehqje5gjrhmhcfhma
    ONTO m1x4x4bvfxok6z2rt5gxpa74zwd6owzf3nnysmd563n6nugvit4z3a
{
  ALTER TYPE default::Chat {
      ALTER TRIGGER get_title USING (WITH
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
          (std::net::http::schedule_request('http://127.0.0.1:8000/get_title', method := std::net::http::Method.POST, headers := [('Content-Type', 'application/json')], body := std::to_bytes(std::to_str(std::json_object_pack({('chat_id', <std::json>__new__.id), ('messages', <std::json>messages_body)})))) IF (__new__.title = 'Untitled') ELSE {})
      );
  };
};
