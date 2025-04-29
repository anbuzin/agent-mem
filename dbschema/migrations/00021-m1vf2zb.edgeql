CREATE MIGRATION m1vf2zbas6zbwxnu6mzgjncfefw4ideezxhlydnxddn5pdnmaarzdq
    ONTO m1uz7ahh73rbvdoj4lwcsk56dbcraf5f6mov4e5lolslrpdu2q2xhq
{
  ALTER TYPE default::Chat {
      CREATE PROPERTY created_at: std::datetime {
          SET default := (std::datetime_current());
      };
  };
};
