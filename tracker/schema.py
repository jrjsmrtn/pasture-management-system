#
# TRACKER SCHEMA
#

# Class automatically gets these properties:
#   creation = Date()
#   activity = Date()
#   creator = Link('user')
#   actor = Link('user')

# Priorities
pri = Class(db, "priority", name=String(), order=Number())
pri.setkey("name")
pri.setlabelprop("name")
pri.setorderprop("order")

# Statuses
stat = Class(db, "status", name=String(), order=Number())
stat.setkey("name")
stat.setlabelprop("name")
stat.setorderprop("order")

# Keywords
keyword = Class(db, "keyword", name=String())
keyword.setkey("name")
keyword.setlabelprop("name")
keyword.setorderprop("name")

# User-defined saved searches
query = Class(db, "query", klass=String(), name=String(), url=String(), private_for=Link("user"))
query.setlabelprop("name")
query.setorderprop("name")

# Change Management Classes

# Change priorities (separate from issue priorities for flexibility)
changepriority = Class(db, "changepriority", name=String(), order=Number())
changepriority.setkey("name")
changepriority.setlabelprop("name")
changepriority.setorderprop("order")

# Change categories for classification
changecategory = Class(db, "changecategory", name=String(), order=Number())
changecategory.setkey("name")
changecategory.setlabelprop("name")
changecategory.setorderprop("order")

# Change statuses for ITIL workflow
changestatus = Class(db, "changestatus", name=String(), order=Number())
changestatus.setkey("name")
changestatus.setlabelprop("name")
changestatus.setorderprop("order")

# CMDB (Configuration Management Database) Classes

# CI types for classification
citype = Class(db, "citype", name=String(), order=Number())
citype.setkey("name")
citype.setlabelprop("name")
citype.setorderprop("order")

# CI statuses for lifecycle management
cistatus = Class(db, "cistatus", name=String(), order=Number())
cistatus.setkey("name")
cistatus.setlabelprop("name")
cistatus.setorderprop("order")

# CI criticality levels
cicriticality = Class(db, "cicriticality", name=String(), order=Number())
cicriticality.setkey("name")
cicriticality.setlabelprop("name")
cicriticality.setorderprop("order")

# CI relationship types
cirelationshiptype = Class(db, "cirelationshiptype", name=String(), order=Number())
cirelationshiptype.setkey("name")
cirelationshiptype.setlabelprop("name")
cirelationshiptype.setorderprop("order")

# add any additional database schema configuration here

user = Class(
    db,
    "user",
    username=String(),
    password=Password(),
    address=String(),
    realname=String(),
    phone=String(),
    organisation=String(),
    alternate_addresses=String(),
    queries=Multilink("query"),
    roles=String(),  # comma-separated string of Role names
    timezone=String(),
)
user.setkey("username")
user.setlabelprop("username")
user.setorderprop("username")
db.security.addPermission(
    name="Register", klass="user", description="User is allowed to register new user"
)

# FileClass automatically gets this property in addition to the Class ones:
#   content = String()    [saved to disk in <tracker home>/db/files/]
#   type = String()       [MIME type of the content, default 'text/plain']
msg = FileClass(
    db,
    "msg",
    author=Link("user", do_journal="no"),
    recipients=Multilink("user", do_journal="no"),
    date=Date(),
    summary=String(indexme='yes'),  # Summary is searchable
    files=Multilink("file"),
    messageid=String(),
    inreplyto=String(),
)
msg.setlabelprop("summary")
msg.setorderprop("date")

file = FileClass(db, "file", name=String())
file.setlabelprop("name")
file.setorderprop("name")

# IssueClass automatically gets these properties in addition to the Class ones:
#   title = String()
#   messages = Multilink("msg")
#   files = Multilink("file")
#   nosy = Multilink("user")
#   superseder = Multilink("issue")
issue = IssueClass(
    db,
    "issue",
    assignedto=Link("user"),
    keyword=Multilink("keyword"),
    priority=Link("priority"),
    status=Link("status"),
    affected_cis=Multilink("ci"),  # CIs affected by this issue
)
issue.setlabelprop("title")
issue.setorderprop("id")

# Change Request class - ITIL Change Management
# Inherits: title, messages, files, nosy from IssueClass
change = IssueClass(
    db,
    "change",
    description=String(indexme='yes'),  # Detailed description - searchable
    justification=String(indexme='yes'),  # Business justification - searchable
    impact=String(indexme='yes'),  # Impact assessment - searchable
    risk=String(indexme='yes'),  # Risk assessment - searchable
    assignedto=Link("user"),  # Change owner
    priority=Link("changepriority"),  # Change priority
    category=Link("changecategory"),  # Change category
    status=Link("changestatus"),  # Change workflow status
    related_issues=Multilink("issue"),  # Issues this change addresses
    target_cis=Multilink("ci"),  # CIs affected by this change
)
change.setlabelprop("title")
change.setorderprop("id")

# Configuration Item class - CMDB
# Base CI with common attributes
ci = Class(
    db,
    "ci",
    name=String(indexme='yes'),  # CI name (required) - searchable
    type=Link("citype"),  # CI type (server, network, storage, etc.)
    status=Link("cistatus"),  # Lifecycle status
    location=String(indexme='yes'),  # Physical/logical location - searchable
    owner=Link("user"),  # CI owner/responsible person
    criticality=Link("cicriticality"),  # Business criticality
    description=String(indexme='yes'),  # CI description - searchable
    # Server-specific attributes
    cpu_cores=Number(),  # Number of CPU cores
    ram_gb=Number(),  # RAM in GB
    os=String(),  # Operating system
    ip_address=String(),  # IP address - not indexed for FTS
    # Network device attributes
    ports=Number(),  # Number of ports
    # Storage attributes
    capacity_gb=Number(),  # Storage capacity in GB
    # Software/Service attributes
    version=String(),  # Software version
    vendor=String(indexme='yes'),  # Vendor/manufacturer - searchable
    # Relationships
    related_issues=Multilink("issue"),  # Issues affecting this CI
    related_changes=Multilink("change"),  # Changes targeting this CI
)
ci.setlabelprop("name")
ci.setorderprop("name")

# CI Relationship class - for modeling dependencies
cirelationship = Class(
    db,
    "cirelationship",
    source_ci=Link("ci"),  # Source CI
    relationship_type=Link("cirelationshiptype"),  # Type of relationship
    target_ci=Link("ci"),  # Target CI
    description=String(indexme='yes'),  # Optional description - searchable
)
cirelationship.setlabelprop("id")
cirelationship.setorderprop("id")

#
# TRACKER SECURITY SETTINGS
#
# See the configuration and customisation document for information
# about security setup.

#
# REGULAR USERS
#
# Give the regular users access to the web and email interface
db.security.addPermissionToRole("User", "Web Access")
db.security.addPermissionToRole("User", "Email Access")
db.security.addPermissionToRole("User", "Rest Access")
db.security.addPermissionToRole("User", "Xmlrpc Access")

# Assign the access and edit Permissions for issue, file and message
# to regular users now
for cl in "issue", "file", "msg", "keyword", "change", "ci", "cirelationship":
    db.security.addPermissionToRole("User", "View", cl)
    db.security.addPermissionToRole("User", "Edit", cl)
    db.security.addPermissionToRole("User", "Create", cl)
for cl in (
    "priority",
    "status",
    "changepriority",
    "changecategory",
    "changestatus",
    "citype",
    "cistatus",
    "cicriticality",
    "cirelationshiptype",
):
    db.security.addPermissionToRole("User", "View", cl)

# May users view other user information? Comment these lines out
# if you don't want them to
p = db.security.addPermission(
    name="View",
    klass="user",
    properties=("id", "organisation", "phone", "realname", "timezone", "username"),
)
db.security.addPermissionToRole("User", p)


# Users should be able to edit their own details -- this permission is
# limited to only the situation where the Viewed or Edited item is their own.
def own_record(db, userid, itemid):
    """Determine whether the userid matches the item being accessed."""
    return userid == itemid


p = db.security.addPermission(
    name="View",
    klass="user",
    check=own_record,
    description="User is allowed to view their own user details",
)
db.security.addPermissionToRole("User", p)
p = db.security.addPermission(
    name="Edit",
    klass="user",
    check=own_record,
    properties=(
        "username",
        "password",
        "address",
        "realname",
        "phone",
        "organisation",
        "alternate_addresses",
        "queries",
        "timezone",
    ),
    description="User is allowed to edit their own user details",
)
db.security.addPermissionToRole("User", p)


# Users should be able to edit and view their own queries. They should also
# be able to view any marked as not private. They should not be able to
# edit others' queries, even if they're not private
def view_query(db, userid, itemid):
    private_for = db.query.get(itemid, "private_for")
    if not private_for:
        return True
    return userid == private_for


def edit_query(db, userid, itemid):
    return userid == db.query.get(itemid, "creator")


p = db.security.addPermission(
    name="View",
    klass="query",
    check=view_query,
    description="User is allowed to view their own and public queries",
)
db.security.addPermissionToRole("User", p)
p = db.security.addPermission(name="Search", klass="query")
db.security.addPermissionToRole("User", p)
p = db.security.addPermission(
    name="Edit",
    klass="query",
    check=edit_query,
    description="User is allowed to edit their queries",
)
db.security.addPermissionToRole("User", p)
p = db.security.addPermission(
    name="Retire",
    klass="query",
    check=edit_query,
    description="User is allowed to retire their queries",
)
db.security.addPermissionToRole("User", p)
p = db.security.addPermission(
    name="Restore",
    klass="query",
    check=edit_query,
    description="User is allowed to restore their queries",
)
db.security.addPermissionToRole("User", p)
p = db.security.addPermission(
    name="Create", klass="query", description="User is allowed to create queries"
)
db.security.addPermissionToRole("User", p)


#
# ANONYMOUS USER PERMISSIONS
#
# Let anonymous users access the web interface. Note that almost all
# trackers will need this Permission. The only situation where it's not
# required is in a tracker that uses an HTTP Basic Authenticated front-end.
db.security.addPermissionToRole("Anonymous", "Web Access")

# Let anonymous users access the email interface (note that this implies
# that they will be registered automatically, hence they will need the
# "Register" user Permission below)
# This is disabled by default to stop spam from auto-registering users on
# public trackers.
# db.security.addPermissionToRole('Anonymous', 'Email Access')

# Assign the appropriate permissions to the anonymous user's Anonymous
# Role. Choices here are:
# - Allow anonymous users to register
db.security.addPermissionToRole("Anonymous", "Register", "user")

# Allow anonymous users access to view issues (and the related, linked
# information)
for cl in (
    "issue",
    "file",
    "msg",
    "keyword",
    "priority",
    "status",
    "change",
    "changepriority",
    "changecategory",
    "changestatus",
    "ci",
    "cirelationship",
    "citype",
    "cistatus",
    "cicriticality",
    "cirelationshiptype",
):
    db.security.addPermissionToRole("Anonymous", "View", cl)

# Allow the anonymous user to use the "Show Unassigned" search.
# It acts like "Show Open" if this permission is not available.
# If you are running a tracker that does not allow read access for
# anonymous, you should remove this entry as it can be used to perform
# a username guessing attack against a roundup install.
p = db.security.addPermission(name="Search", klass="user")
db.security.addPermissionToRole("Anonymous", p)

# [OPTIONAL]
# Allow anonymous users access to create or edit "issue" items (and the
# related file and message items)
# for cl in 'issue', 'file', 'msg':
#   db.security.addPermissionToRole('Anonymous', 'Create', cl)
#   db.security.addPermissionToRole('Anonymous', 'Edit', cl)


# vim: set filetype=python sts=4 sw=4 et si :
# SHA: 74053bfdcdf9202e94c121dd9241b0bd9e893dbb
