CREATE OR REPLACE FUNCTION create_preference(preference_name TEXT,
                                             preference_rules TEXT)
RETURNS BOOL
LANGUAGE plpythonu AS $$
    from sys import path
    UPREFSQL_PATH = '/usr/lib/postgresql/libuprefsql/uprefsql'
    UPREFSQL_TABLE = '__preferences'
    if UPREFSQL_PATH not in path:
        path.append(UPREFSQL_PATH)
    from cp_theory import CPTheory

    # Check if parameters are valid
    if preference_name is None or preference_rules is None \
    or preference_name == '' or preference_rules == '':
        plpy.notice('Invalid parameters')
        return False

    cpt = CPTheory(preference_rules)
    consistent =  cpt.consistent
    if consistent:
        # Check if theory already exists
        r = plpy.execute('''SELECT * FROM {table}
                    WHERE preference_name = {pref_name}'''.format(
                        table=UPREFSQL_TABLE,
                        pref_name=plpy.quote_literal(preference_name)))
        # If theory already exists, then delete it
        if len(r) > 0:
            plpy.execute('''DELETE FROM {table}
                    WHERE preference_name = {pref_name}'''.format(
                        table=UPREFSQL_TABLE,
                        pref_name=plpy.quote_literal(preference_name)
                        ))
        # Store theory
        plpy.execute('''INSERT INTO {table}
                VALUES ({pref_name}, {pref_rules})'''.format(
                    table=UPREFSQL_TABLE,
                    pref_name=plpy.quote_literal(preference_name),
                    pref_rules=plpy.quote_literal(str(cpt))
                 ))
    else:
        plpy.notice('Inconsistent preferences!')
    del cpt
    return consistent
$$;
