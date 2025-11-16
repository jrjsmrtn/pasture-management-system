/*
 * SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
 * SPDX-License-Identifier: MIT
 *
 * C4 Architecture Model for Pasture Management System
 *
 * This model describes the architecture of PMS, an ITIL-inspired
 * issue/change/CMDB management system built on Roundup Issue Tracker.
 *
 * View online: docker run --rm -p 8080:8080 -v "$(pwd):/usr/local/structurizr" structurizr/lite
 */

workspace "Pasture Management System" "ITIL-inspired issue tracking and change management for homelab sysadmins" {

    model {
        # People and External Systems
        sysadmin = person "Homelab Sysadmin" "Manages homelab infrastructure, tracks issues, and implements changes" "Sysadmin"
        developer = person "BDD Developer" "Learns BDD/Behave/Playwright practices from this project" "Developer"

        emailSystem = softwareSystem "Email System" "Sends notifications about issues and changes" "External System"
        browser = softwareSystem "Web Browser" "User's web browser for accessing the tracker" "External System"

        # Main System
        pms = softwareSystem "Pasture Management System" "ITIL-inspired issue tracking, change management, and CMDB for homelab environments" {
            # Containers
            webApp = container "Roundup Web Application" "Provides web UI for issue tracking, change management, and CMDB" "Python, Roundup, TAL Templates" "Web Application" {
                # Components - Issue Tracking Module
                issueController = component "Issue Controller" "Handles issue CRUD operations and workflow" "Roundup Controller"
                issueView = component "Issue Views" "TAL templates for issue display and forms" "TAL Templates"
                issueWorkflow = component "Issue Workflow Engine" "Manages issue status transitions (new→in-progress→resolved→closed)" "Python Detector"

                # Components - Change Management Module
                changeController = component "Change Controller" "Handles change request CRUD operations" "Roundup Controller"
                changeView = component "Change Views" "TAL templates for change request display" "TAL Templates"
                changeWorkflow = component "Change Workflow Engine" "Manages change status transitions (proposed→approved→scheduled→implemented→closed)" "Python Detector"

                # Components - CMDB Module (planned)
                cmdbController = component "CMDB Controller" "Manages configuration items" "Roundup Controller" "Future"
                cmdbView = component "CMDB Views" "TAL templates for CI display" "TAL Templates" "Future"

                # Components - Shared Infrastructure
                authHandler = component "Authentication Handler" "Manages user authentication and sessions" "Roundup Security"
                notificationEngine = component "Notification Engine" "Sends email notifications on issue/change updates" "Python Detector"
                restAPI = component "REST API" "Provides JSON API for programmatic access" "Roundup REST"
            }

            database = container "Tracker Database" "Stores issues, changes, users, and CMDB data" "AnyDBM/SQLite/PostgreSQL" "Database"

            cliTool = container "CLI Tool" "Command-line interface for tracker administration" "Python, roundup-admin" "CLI"
        }

        # Relationships - People to System
        sysadmin -> pms "Tracks issues, manages changes, maintains CMDB using"
        sysadmin -> webApp "Uses web interface"
        sysadmin -> cliTool "Administers using"
        developer -> pms "Studies BDD implementation in"

        # Relationships - System to External
        pms -> emailSystem "Sends notifications using"
        browser -> pms "Accesses via HTTPS"
        browser -> webApp "Accesses"

        # Relationships - Containers
        webApp -> database "Reads from and writes to" "SQL/Python API"
        cliTool -> database "Administers" "Python API"
        webApp -> emailSystem "Sends notifications via" "SMTP"

        # Relationships - Components to Database
        issueController -> database "Stores/retrieves issues"
        issueWorkflow -> database "Updates issue status"
        changeController -> database "Stores/retrieves changes"
        changeWorkflow -> database "Updates change status"
        cmdbController -> database "Stores/retrieves CIs"
        authHandler -> database "Validates credentials"

        # Relationships - Component Dependencies
        issueView -> issueController "Uses"
        issueController -> issueWorkflow "Triggers"
        issueWorkflow -> notificationEngine "Notifies on status change"

        changeView -> changeController "Uses"
        changeController -> changeWorkflow "Triggers"
        changeWorkflow -> notificationEngine "Notifies on status change"

        cmdbView -> cmdbController "Uses"

        restAPI -> issueController "Exposes"
        restAPI -> changeController "Exposes"
        restAPI -> cmdbController "Exposes"

        notificationEngine -> emailSystem "Sends via SMTP"

        # BDD Test Infrastructure (Development View)
        testSystem = softwareSystem "BDD Test Infrastructure" "Automated testing using Behave and Playwright" "Testing" {
            behaveRunner = container "Behave Runner" "Executes Gherkin scenarios" "Python, Behave"
            playwrightDriver = container "Playwright Driver" "Automates web UI testing" "Python, Playwright"
            stepDefinitions = container "Step Definitions" "Implements Gherkin steps" "Python"
        }

        developer -> testSystem "Runs BDD tests using"
        developer -> behaveRunner "Runs BDD tests using"
        testSystem -> pms "Tests" "Web UI, CLI, REST API"
        behaveRunner -> stepDefinitions "Executes"
        stepDefinitions -> playwrightDriver "Uses for Web UI tests"
        playwrightDriver -> browser "Controls"
    }

    views {
        # System Context - Level 1
        systemContext pms "SystemContext" {
            include *
            exclude testSystem
            autoLayout
            description "System context diagram showing PMS in the homelab ecosystem"
            properties {
                structurizr.groups false
            }
        }

        # Container - Level 2
        container pms "Containers" {
            include *
            autoLayout
            description "Container diagram showing the main components of PMS"
        }

        # Component - Level 3 (Issue Tracking)
        component webApp "IssueTrackingComponents" {
            include issueController issueView issueWorkflow notificationEngine authHandler restAPI database emailSystem
            autoLayout
            description "Component diagram for Issue Tracking module"
        }

        # Component - Level 3 (Change Management)
        component webApp "ChangeManagementComponents" {
            include changeController changeView changeWorkflow notificationEngine authHandler restAPI database emailSystem
            autoLayout
            description "Component diagram for Change Management module"
        }

        # Development/Testing View
        systemContext testSystem "TestingContext" {
            include *
            autoLayout
            description "BDD testing infrastructure and its relationship to PMS"
        }

        # Dynamic diagram - Issue Workflow (Container level)
        dynamic webApp "IssueWorkflow" "Creating and resolving an issue" {
            issueView -> issueController "1. Submits create request"
            issueController -> database "2. Stores issue (status=new)"
            issueController -> issueWorkflow "3. Triggers workflow"
            issueWorkflow -> notificationEngine "4. Notifies assigned user"
            notificationEngine -> emailSystem "5. Sends email"

            issueView -> issueController "6. Submits status update"
            issueController -> issueWorkflow "7. Validates transition"
            issueWorkflow -> database "8. Updates status"
            issueWorkflow -> notificationEngine "9. Notifies watchers"

            autoLayout
            description "Step-by-step flow of creating and updating an issue"
        }

        # Dynamic diagram - BDD Test Execution
        dynamic testSystem "BDDTestExecution" "Running a BDD scenario" {
            developer -> behaveRunner "1. Runs 'behave features/'"
            behaveRunner -> stepDefinitions "2. Executes step definitions"
            stepDefinitions -> playwrightDriver "3. Automates browser (for @web-ui)"
            playwrightDriver -> browser "4. Controls browser"
            browser -> pms "5. Interacts with PMS"
            pms -> browser "6. Renders response"
            browser -> playwrightDriver "7. Returns page state"
            playwrightDriver -> stepDefinitions "8. Verifies assertions"
            stepDefinitions -> behaveRunner "9. Reports pass/fail"

            autoLayout
            description "BDD test execution flow for web UI scenarios"
        }

        # Styling
        styles {
            element "Person" {
                shape Person
                background #08427b
                color #ffffff
            }
            element "Sysadmin" {
                background #1168bd
            }
            element "Developer" {
                background #6cb33e
            }
            element "Software System" {
                background #1168bd
                color #ffffff
            }
            element "External System" {
                background #999999
                color #ffffff
            }
            element "Testing" {
                background #6cb33e
                color #ffffff
            }
            element "Container" {
                background #438dd5
                color #ffffff
            }
            element "Web Application" {
                shape WebBrowser
            }
            element "Database" {
                shape Cylinder
            }
            element "CLI" {
                shape Box
            }
            element "Component" {
                background #85bbf0
                color #000000
            }
            element "Future" {
                background #cccccc
                color #000000
                opacity 50
            }
        }
    }

    configuration {
        # No scope constraint - workspace includes both PMS and test infrastructure
    }
}
