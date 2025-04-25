CREATE MIGRATION m1e3bijurgw5lxlx7lq7mzgijfo4nlulbvyz4lvuccwiqxyr4njmfa
    ONTO m1vyz7gc4pwntp5k5djhqgrpb7y4lhni53q6bsolwfk435fi3yksra
{
  ALTER TYPE default::Chat {
      ALTER TRIGGER summarize USING (SELECT
          std::net::http::schedule_request('http://127.0.0.1:8000/summarize', method := std::net::http::Method.POST, headers := [('Content-Type', 'application/json')], body := std::to_bytes(std::to_str(std::json_object_pack({('messages', <std::json>__new__.history.messages.body), ('chat_id', <std::json>__new__.id)}))))
      );
  };
};
