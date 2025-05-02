CREATE MIGRATION m1nwe3h2r5cnhubajtvzu72atjdazursnelnrygjtaj7i5cbudxfqa
    ONTO m14ulwmd2xqv67c6kphkkgzm5irtqjzybbpaqtcntejjzbvjwdlwtq
{
  ALTER TYPE default::Fact {
      DROP INDEX ext::ai::index(embedding_model := 'text-embedding-3-small') ON (.value);
  };
  ALTER TYPE default::Fact {
      CREATE DEFERRED INDEX ext::ai::index(embedding_model := 'text-embedding-3-small') ON (((.key ++ ': ') ++ .value));
  };
};
