# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

Feature: Email Security Controls
  As a homelab sysadmin
  I want secure email gateway controls
  So that my tracker is protected from email-based threats

  Background:
    Given the Roundup tracker is running
    And the admin user exists with email "roundup-admin@localhost"

  @security @email
  Scenario: Unknown sender silently rejected (prevents user enumeration)
    Given no user exists with email "attacker@external.com"
    And I compose an email with:
      | field   | value                              |
      | from    | attacker@external.com              |
      | to      | issue_tracker@localhost            |
      | subject | Reconnaissance attempt             |
      | body    | Probing for user enumeration       |
    When I send the email to the mail gateway
    Then no user should be created with email "attacker@external.com"
    And no issue should be created
    # Note: Silent rejection prevents attackers from discovering valid user addresses

  @security @email
  Scenario: Invalid issue ID silently rejected (prevents ID enumeration)
    Given I compose an email with:
      | field   | value                                  |
      | from    | roundup-admin@localhost                |
      | to      | issue_tracker@localhost                |
      | subject | [issue99999] Probing non-existent ID   |
      | body    | Testing for issue ID enumeration       |
    When I send the email to the mail gateway
    Then no issue should be created
    And no error message should be sent
    # Note: Silent rejection prevents attackers from discovering valid issue IDs

  @security @email @html
  Scenario: HTML email sanitized to prevent XSS
    Given I compose an HTML email with:
      | field   | value                                                  |
      | from    | roundup-admin@localhost                                |
      | to      | issue_tracker@localhost                                |
      | subject | XSS attempt                                            |
      | html    | <p>Test <script>alert('XSS')</script> sanitization</p> |
    When I send the email to the mail gateway
    Then a new issue should be created
    And the issue description should not contain "<script>"
    And the issue description should not contain "alert"
    And the issue description should contain "Test"
    And the issue description should contain "sanitization"
    # Note: HTML is converted to plain text, stripping all tags including script

  @security @email
  Scenario: Malformed subject prefix rejected in strict mode
    Given I compose an email with:
      | field   | value                                      |
      | from    | roundup-admin@localhost                    |
      | to      | issue_tracker@localhost                    |
      | subject | [INVALID_PREFIX123] Malformed subject      |
      | body    | Testing strict subject prefix parsing      |
    When I send the email to the mail gateway
    Then no issue should be created
    # Note: Strict parsing (subject_prefix_parsing = strict) rejects unknown prefixes

  @security @email
  Scenario: Email with only whitespace subject rejected
    Given I compose an email with:
      | field   | value                     |
      | from    | roundup-admin@localhost   |
      | to      | issue_tracker@localhost   |
      | subject |                           |
      | body    | Empty subject test        |
    When I send the email to the mail gateway
    Then no issue should be created
    # Note: Issues require a title, which comes from the subject line

  @security @email @config
  Scenario: PGP-signed email verification (optional feature)
    Given PGP is configured and enabled
    And I compose a PGP-signed email with:
      | field   | value                           |
      | from    | roundup-admin@localhost         |
      | to      | issue_tracker@localhost         |
      | subject | Signed issue                    |
      | body    | This message is cryptographically signed |
    When I send the email to the mail gateway
    Then a new issue should be created
    And the issue should be marked as PGP-verified
    # Note: This scenario requires PGP configuration (optional for homelabs)
