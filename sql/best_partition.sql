CREATE OR REPLACE FUNCTION most_preferred_partition(preference_name TEXT,
                                          sql TEXT)
RETURNS SETOF RECORD
LANGUAGE plpythonu AS $$
    from sys import path
    UPREFSQL_PATH = '/usr/lib/postgresql/libuprefsql/uprefsql'
    UPREFSQL_TABLE = '__preferences'
    if UPREFSQL_PATH not in path:
        path.append(UPREFSQL_PATH)
    from cp_most_preferred_partition import most_preferred_partition

    # Check if parameters are valid
    if preference_name is None or sql is None \
    or preference_name == '' or sql == '':
        plpy.error('Invalid parameters')

    # Get preference rules
    res = plpy.execute('''SELECT preference_rules
                          FROM {table}
                          WHERE preference_name = {pref_name}'''.format(
                          table=UPREFSQL_TABLE,
                          pref_name=plpy.quote_literal(preference_name)
                       ))
    if len(res) != 1:
        plpy.error('Invalid preference name')
    preference_rules = res[0]['preference_rules']

    # Get tuples from SQL
    tuples_list = plpy.execute(sql)

    return most_preferred_partition(preference_rules, tuples_list)
$$;
