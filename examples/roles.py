from match_variant import Variant


class Role(Variant):
    anonymous: ()
    unauthenticated: (str, str)
    normal: (str,)
    admin: (
        str,
        dict[str, bool],
    )


anon = Role.anonymous()
needs_to_login = Role.unauthenticated("chris", "bad password")
logged_in = Role.normal("jessie")
super = Role.admin("morgan", {"can_edit": True})
viewer = Role.admin("alex", {"can_edit": False})


for user in anon, needs_to_login, logged_in, super, viewer:
    match user:
        case Role.anonymous():
            print("User has not provided credentials")
        case Role.unauthenticated(name, pw):
            print(f"User {name} needs to log in with {pw}")
        case Role.normal(name):
            print(f"User {name} is logged in")
        case Role.admin(name, {"can_edit": editable}) if editable:
            print(f"User {name} can edit")
        case Role.admin(name, {"can_edit": editable}) if not editable:
            print(f"User {name} can view but not edit")
