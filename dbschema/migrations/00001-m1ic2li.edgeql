CREATE MIGRATION m1ic2li6sz33lw5iqw5u22e4vikouosv3mjdztf2q6blkpd2jqepea
    ONTO initial
{
  CREATE FUTURE simple_scoping;
  CREATE TYPE default::Message {
      CREATE PROPERTY body: std::str;
      CREATE PROPERTY created_at: std::datetime {
          SET default := (std::datetime_current());
      };
      CREATE PROPERTY llm_role: std::str;
  };
  CREATE TYPE default::History {
      CREATE MULTI LINK messages: default::Message;
  };
  CREATE TYPE default::Chat {
      CREATE MULTI LINK archive: default::Message;
      CREATE LINK history: default::History {
          CREATE REWRITE
              UPDATE 
              USING (UPDATE
                  default::History
              FILTER
                  (.id = __subject__.history.id)
              SET {
                  messages := DISTINCT ((__subject__.history.messages UNION __old__.history.messages))
              });
      };
      CREATE TRIGGER summarize
          AFTER UPDATE 
          FOR EACH DO (SELECT
              std::net::http::schedule_request('http://127.0.0.1:8000/summarize', method := std::net::http::Method.POST, headers := [('Content-Type', 'application/json')], body := std::to_bytes(std::to_str(std::json_object_pack({('messages', <std::json>__new__.history.messages), ('chat_id', <std::json>__new__.id)}))))
          );
  };
};
