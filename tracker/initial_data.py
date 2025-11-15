#
# TRACKER INITIAL PRIORITY AND STATUS VALUES
#
pri = db.getclass('priority')
pri.create(name=''"critical", order="1")
pri.create(name=''"urgent", order="2")
pri.create(name=''"bug", order="3")
pri.create(name=''"feature", order="4")
pri.create(name=''"wish", order="5")

# ITIL-inspired workflow statuses
stat = db.getclass('status')
stat.create(name=''"new", order="1")         # Initial state for new issues
stat.create(name=''"in-progress", order="2") # Work has started
stat.create(name=''"resolved", order="3")    # Issue fixed, awaiting verification
stat.create(name=''"closed", order="4")      # Issue verified and closed

# create the two default users
user = db.getclass('user')
user.create(username="admin", password=adminpw,
    address=admin_email, roles='Admin')
user.create(username="anonymous", roles='Anonymous')

# add any additional database creation steps here - but only if you
# haven't initialised the database with the admin "initialise" command


# vim: set filetype=python sts=4 sw=4 et si
#SHA: f52a98b31599aa459a82a7852175660cf9cdcd6b
