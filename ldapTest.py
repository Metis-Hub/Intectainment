from ldap3 import Connection, SUBTREE

conn = Connection("ldap://localhost", "cn=admin,dc=example,dc=org", "admin", auto_bind=True)


conn.search("cn=user,ou=groups,dc=example,dc=org", search_filter = '(objectClass=*)', search_scope = SUBTREE, attributes = ["memberUid"])

for entry in conn.entries:
    for member in entry.memberUid.values:
        print(f"{member}")