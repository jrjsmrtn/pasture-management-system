#
# TRACKER INITIAL PRIORITY AND STATUS VALUES
#
pri = db.getclass("priority")
pri.create(name="critical", order="1")
pri.create(name="urgent", order="2")
pri.create(name="bug", order="3")
pri.create(name="feature", order="4")
pri.create(name="wish", order="5")

# ITIL-inspired workflow statuses
stat = db.getclass("status")
stat.create(name="new", order="1")  # Initial state for new issues
stat.create(name="in-progress", order="2")  # Work has started
stat.create(name="resolved", order="3")  # Issue fixed, awaiting verification
stat.create(name="closed", order="4")  # Issue verified and closed

# Change Management - Priorities
changepri = db.getclass("changepriority")
changepri.create(name="low", order="1")
changepri.create(name="medium", order="2")
changepri.create(name="high", order="3")
changepri.create(name="critical", order="4")

# Change Management - Categories
changecat = db.getclass("changecategory")
changecat.create(name="software", order="1")
changecat.create(name="hardware", order="2")
changecat.create(name="configuration", order="3")
changecat.create(name="network", order="4")

# Change Management - ITIL workflow statuses
changestat = db.getclass("changestatus")
changestat.create(name="planning", order="1")  # Change request being planned
changestat.create(name="approved", order="2")  # Change approved for implementation
changestat.create(name="implementing", order="3")  # Change implementation in progress
changestat.create(name="completed", order="4")  # Change successfully completed
changestat.create(name="cancelled", order="5")  # Change cancelled/rejected

# CMDB - CI Types
citype_class = db.getclass("citype")
citype_class.create(name="Server", order="1")
citype_class.create(name="Network Device", order="2")
citype_class.create(name="Storage", order="3")
citype_class.create(name="Software", order="4")
citype_class.create(name="Service", order="5")
citype_class.create(name="Virtual Machine", order="6")

# CMDB - CI Lifecycle Statuses
cistatus_class = db.getclass("cistatus")
cistatus_class.create(name="Planning", order="1")
cistatus_class.create(name="Ordered", order="2")
cistatus_class.create(name="In Stock", order="3")
cistatus_class.create(name="Deployed", order="4")
cistatus_class.create(name="Active", order="5")
cistatus_class.create(name="Maintenance", order="6")
cistatus_class.create(name="Retired", order="7")

# CMDB - CI Criticality Levels
cicrit_class = db.getclass("cicriticality")
cicrit_class.create(name="Very Low", order="1")
cicrit_class.create(name="Low", order="2")
cicrit_class.create(name="Medium", order="3")
cicrit_class.create(name="High", order="4")
cicrit_class.create(name="Very High", order="5")

# CMDB - CI Relationship Types
cirel_class = db.getclass("cirelationshiptype")
cirel_class.create(name="Runs On", order="1")  # VM runs on server
cirel_class.create(name="Hosts", order="2")  # Server hosts VM (inverse of Runs On)
cirel_class.create(name="Depends On", order="3")  # Service depends on another CI
cirel_class.create(name="Required By", order="4")  # Inverse of Depends On
cirel_class.create(name="Connects To", order="5")  # Network connection
cirel_class.create(name="Contains", order="6")  # Physical containment
cirel_class.create(name="Contained By", order="7")  # Inverse of Contains

# create the two default users
user = db.getclass("user")
user.create(username="admin", password=adminpw, address=admin_email, roles="Admin")
user.create(username="anonymous", roles="Anonymous")

# add any additional database creation steps here - but only if you
# haven't initialised the database with the admin "initialise" command


# vim: set filetype=python sts=4 sw=4 et si
# SHA: f52a98b31599aa459a82a7852175660cf9cdcd6b
