CREATE OR REPLACE FUNCTION mostk_preferred(preference_name TEXT,
                                           k INTEGER, sql TEXT)
RETURNS SETOF RECORD
LANGUAGE plpythonu AS $$
    from sys import path
    UPREFSQL_PATH = '/usr/lib/postgresql/libuprefsql/uprefsql'
    UPREFSQL_TABLE = '__preferences'
    if UPREFSQL_PATH not in path:
        path.append(UPREFSQL_PATH)
    from cp_most_preferred import most_preferred
    from cp_mostk_preferred import mostk_preferred

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

    if k == -1:
        return most_preferred(preference_rules, tuples_list)
    else:
        return mostk_preferred(preference_rules, k, tuples_list)
$$;
