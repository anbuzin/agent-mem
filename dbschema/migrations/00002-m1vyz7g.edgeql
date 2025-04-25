CREATE MIGRATION m1vyz7gc4pwntp5k5djhqgrpb7y4lhni53q6bsolwfk435fi3yksra
    ONTO m1ic2li6sz33lw5iqw5u22e4vikouosv3mjdztf2q6blkpd2jqepea
{
  ALTER TYPE default::Chat {
      ALTER LINK history {
          DROP REWRITE
              UPDATE ;
          };
      };
};
