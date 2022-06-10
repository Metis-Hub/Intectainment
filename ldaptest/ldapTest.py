from ldap3 import Connection, Server, SUBTREE
import ast, dotenv, os

dotenv.load_dotenv()


# create server object
server = Server("ldap://localhost")

# load role: level mapping from env variable
roles = os.getenv("INTECTAINMENT_LDAP_PERMISSIONS")
print(roles)
if roles:
    roles = {k: v for k, v in sorted(ast.literal_eval(roles).items(), key=lambda item: item[1], reverse=True)}
else:
    roles = {}
print(roles)


class User:
    def __init__(self, uid, permissionLevel=0):
        self.uid = uid
        self.permissionLevel = permissionLevel
        pass
    
    @staticmethod
    def login(usercn: str, password: str):
        try:
            conn = Connection(server, self.getUserDN(usercn), password, auto_bind=True)
        except:
            return False
        
        user = User(conn.entries[0].uid)
        
        for group, permission in roles.items():
            conn.search(
                search_base=User.getGroupDN(group),
                search_filter='(objectClass=group)',
                search_scope='SUBTREE',
                attributes = ['member']
            )

        
        return user
    




    @staticmethod
    def getUserDN(user: str):
        return f"{os.getenv('INTECTAINMENT_LDAP_USER_ID')}={user},{os.getenv('INTECTAINMENT_LDAP_USER_DN')},{os.getenv('INTECTAINMENT_LDAP_ROOT')}"

    @staticmethod
    def getGroupDN(group: str):
        return f"{os.getenv('INTECTAINMENT_LDAP_GROUP_ID')}={group},{os.getenv('INTECTAINMENT_LDAP_GROUP_DN')},{os.getenv('INTECTAINMENT_LDAP_ROOT')}"





user = User.login("Jeffray Jefferson", "1234")