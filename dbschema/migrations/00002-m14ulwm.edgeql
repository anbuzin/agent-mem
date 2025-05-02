CREATE MIGRATION m14ulwmd2xqv67c6kphkkgzm5irtqjzybbpaqtcntejjzbvjwdlwtq
    ONTO m1d3qolbbuunjhc442een6w5dqv4ca3o5ec33pnf56mdqkcyiocyya
{
  CREATE TYPE default::Fact {
      CREATE PROPERTY value: std::str;
      CREATE DEFERRED INDEX ext::ai::index(embedding_model := 'text-embedding-3-small') ON (.value);
      CREATE LINK from_message: default::Message;
      CREATE PROPERTY key: std::str {
          CREATE CONSTRAINT std::exclusive;
      };
      CREATE PROPERTY body := (((.key ++ ': ') ++ .value));
  };
  CREATE TYPE default::Prompt {
      CREATE LINK from_message: default::Message;
      CREATE PROPERTY key: std::str {
          CREATE CONSTRAINT std::exclusive;
      };
      CREATE PROPERTY value: std::str;
      CREATE PROPERTY body := (((.key ++ ': ') ++ .value));
  };
  CREATE TYPE default::Resource {
      CREATE PROPERTY body: std::str;
      CREATE DEFERRED INDEX ext::ai::index(embedding_model := 'text-embedding-3-small') ON (.body);
  };
};
