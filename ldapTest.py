from ldap3 import Connection, SUBTREE, ALL

conn = Connection("ldap://localhost:1389", "cn=admin,dc=intecsoft,dc=de", "adminpassword", auto_bind=True)

conn.search("dc=intecsoft,dc=de", search_filter = '(objectClass=person)', search_scope = SUBTREE, attributes = [ "cn"])