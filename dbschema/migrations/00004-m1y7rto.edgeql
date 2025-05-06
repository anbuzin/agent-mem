CREATE MIGRATION m1y7rtojrz4ixm2alxuthgtxlwg455w6z72q4dzj24nzcmfqsaidkq
    ONTO m1nwe3h2r5cnhubajtvzu72atjdazursnelnrygjtaj7i5cbudxfqa
{
  ALTER TYPE default::Message {
      CREATE PROPERTY tool_args: std::json;
      CREATE PROPERTY tool_name: std::str;
  };
};
