CREATE MIGRATION m1ljqptjmegd5q3afkj4cu2wgxc5qacsdbp6llotzbube46jomvdva
    ONTO m1y7rtojrz4ixm2alxuthgtxlwg455w6z72q4dzj24nzcmfqsaidkq
{
  ALTER TYPE default::Chat {
      CREATE TRIGGER extract
          AFTER UPDATE 
          FOR EACH DO (SELECT
              std::net::http::schedule_request('http://127.0.0.1:8000/extract', method := std::net::http::Method.POST, headers := [('Content-Type', 'application/json')], body := std::to_bytes(std::to_str(std::json_object_pack({('chat_id', <std::json>__new__.id)}))))
          );
  };
};
