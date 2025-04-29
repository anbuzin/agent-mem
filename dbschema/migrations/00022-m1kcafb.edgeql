CREATE MIGRATION m1kcafb6fukkmqhmtizxodhakx52xmq3a7754ktnszeug6wlyvjfwa
    ONTO m1vf2zbas6zbwxnu6mzgjncfefw4ideezxhlydnxddn5pdnmaarzdq
{
  ALTER TYPE default::Chat {
      CREATE PROPERTY title: std::str {
          SET default := 'Untitled';
      };
  };
};
