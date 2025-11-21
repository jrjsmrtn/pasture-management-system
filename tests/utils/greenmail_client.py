# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

"""
GreenMail client for BDD email testing.

This module provides a Python client for interacting with GreenMail email server
in BDD tests, supporting SMTP sending and IMAP retrieval.
"""

import email
import imaplib
import smtplib
from email.message import EmailMessage
from typing import Optional


class GreenMailClient:
    """
    Client for interacting with GreenMail email server.

    GreenMail provides a test email server with SMTP, IMAP, and POP3 support.
    This client simplifies sending and receiving emails in BDD tests.
    """

    def __init__(
        self,
        smtp_host: str = "localhost",
        smtp_port: int = 3025,
        imap_host: str = "localhost",
        imap_port: int = 3143,
    ):
        """
        Initialize GreenMail client.

        Args:
            smtp_host: SMTP server host (default: localhost)
            smtp_port: SMTP server port (default: 3025)
            imap_host: IMAP server host (default: localhost)
            imap_port: IMAP server port (default: 3143)
        """
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.imap_host = imap_host
        self.imap_port = imap_port

    def send_email(
        self,
        from_addr: str,
        to_addr: str,
        subject: str,
        body: str,
        html: Optional[str] = None,
    ) -> None:
        """
        Send an email via SMTP.

        Args:
            from_addr: Sender email address
            to_addr: Recipient email address
            subject: Email subject
            body: Email body (plain text)
            html: Optional HTML body

        Raises:
            smtplib.SMTPException: If sending fails
        """
        msg = EmailMessage()
        msg["From"] = from_addr
        msg["To"] = to_addr
        msg["Subject"] = subject
        msg.set_content(body)

        if html:
            msg.add_alternative(html, subtype="html")

        with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as smtp:
            # GreenMail with auth.disabled still expects login, use the email as both user and pass
            try:
                smtp.login(from_addr, from_addr)
            except smtplib.SMTPException:
                # Login might fail but that's ok for GreenMail with auth disabled
                pass
            smtp.send_message(msg)

    def send_raw_email(self, raw_message: str) -> None:
        """
        Send a raw email message via SMTP.

        Args:
            raw_message: Raw email message string (RFC 2822 format)

        Raises:
            smtplib.SMTPException: If sending fails
        """
        # Parse the raw message to get From and To
        msg = email.message_from_string(raw_message)
        from_addr = msg.get("From", "")
        to_addr = msg.get("To", "")

        with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as smtp:
            # GreenMail with auth.disabled still expects login
            try:
                smtp.login(from_addr, from_addr)
            except smtplib.SMTPException:
                pass
            smtp.sendmail(from_addr, [to_addr], raw_message)

    def get_received_messages(
        self, mailbox: str = "INBOX", user: str = "test@localhost", password: str = "test"
    ) -> list[EmailMessage]:
        """
        Retrieve all messages from an IMAP mailbox.

        Args:
            mailbox: Mailbox name (default: INBOX)
            user: IMAP username (email address)
            password: IMAP password

        Returns:
            List of EmailMessage objects

        Raises:
            imaplib.IMAP4.error: If IMAP operation fails
        """
        messages = []

        with imaplib.IMAP4(self.imap_host, self.imap_port) as imap:
            imap.login(user, password)
            imap.select(mailbox)

            # Search for all messages
            _, message_numbers = imap.search(None, "ALL")

            for num in message_numbers[0].split():
                _, msg_data = imap.fetch(num, "(RFC822)")
                email_body = msg_data[0][1]
                msg = email.message_from_bytes(email_body)
                messages.append(msg)

        return messages

    def get_message_count(
        self, mailbox: str = "INBOX", user: str = "test@localhost", password: str = "test"
    ) -> int:
        """
        Get the number of messages in a mailbox.

        Args:
            mailbox: Mailbox name (default: INBOX)
            user: IMAP username (email address)
            password: IMAP password

        Returns:
            Number of messages in the mailbox

        Raises:
            imaplib.IMAP4.error: If IMAP operation fails
        """
        with imaplib.IMAP4(self.imap_host, self.imap_port) as imap:
            imap.login(user, password)
            imap.select(mailbox)
            _, message_numbers = imap.search(None, "ALL")
            return len(message_numbers[0].split()) if message_numbers[0] else 0

    def clear_mailbox(
        self, mailbox: str = "INBOX", user: str = "test@localhost", password: str = "test"
    ) -> int:
        """
        Delete all messages from a mailbox.

        Args:
            mailbox: Mailbox name (default: INBOX)
            user: IMAP username (email address)
            password: IMAP password

        Returns:
            Number of messages deleted

        Raises:
            imaplib.IMAP4.error: If IMAP operation fails
        """
        deleted_count = 0

        with imaplib.IMAP4(self.imap_host, self.imap_port) as imap:
            imap.login(user, password)
            imap.select(mailbox)

            # Search for all messages
            _, message_numbers = imap.search(None, "ALL")

            if message_numbers[0]:
                for num in message_numbers[0].split():
                    imap.store(num, "+FLAGS", "\\Deleted")
                    deleted_count += 1

                # Permanently delete messages marked for deletion
                imap.expunge()

        return deleted_count

    def wait_for_message(
        self,
        timeout: int = 10,
        mailbox: str = "INBOX",
        user: str = "test@localhost",
        password: str = "test",
    ) -> Optional[EmailMessage]:
        """
        Wait for a message to arrive in the mailbox.

        Args:
            timeout: Maximum time to wait in seconds (default: 10)
            mailbox: Mailbox name (default: INBOX)
            user: IMAP username (email address)
            password: IMAP password

        Returns:
            First EmailMessage if received, None if timeout

        Raises:
            imaplib.IMAP4.error: If IMAP operation fails
        """
        import time

        start_time = time.time()

        while time.time() - start_time < timeout:
            messages = self.get_received_messages(mailbox, user, password)
            if messages:
                return messages[0]
            time.sleep(0.5)

        return None


class GreenMailContainer:
    """
    Helper for managing GreenMail container lifecycle with Podman.

    This class provides methods to start, stop, and check the status of
    a GreenMail container using Podman.
    """

    def __init__(
        self,
        container_name: str = "greenmail-bdd",
        image: str = "docker.io/greenmail/standalone:2.1.7",
        smtp_port: int = 3025,
        imap_port: int = 3143,
        pop3_port: int = 3110,
        api_port: int = 8080,
    ):
        """
        Initialize GreenMail container manager.

        Args:
            container_name: Container name (default: greenmail-bdd)
            image: GreenMail image (default: docker.io/greenmail/standalone:2.1.0-rc-1)
            smtp_port: SMTP port (default: 3025)
            imap_port: IMAP port (default: 3143)
            pop3_port: POP3 port (default: 3110)
            api_port: API port (default: 8080)
        """
        self.container_name = container_name
        self.image = image
        self.smtp_port = smtp_port
        self.imap_port = imap_port
        self.pop3_port = pop3_port
        self.api_port = api_port

    def start(self) -> bool:
        """
        Start the GreenMail container.

        Returns:
            True if started successfully, False otherwise
        """
        import subprocess

        # Stop existing container if running (ignore errors)
        try:
            subprocess.run(
                ["podman", "stop", self.container_name],
                capture_output=True,
                text=True,
                timeout=10,
            )
            # Give time for cleanup
            import time

            time.sleep(1)
        except Exception:
            pass

        # Start new container
        cmd = [
            "podman",
            "run",
            "--rm",
            "-d",
            "--name",
            self.container_name,
            "-p",
            f"{self.smtp_port}:3025",
            "-p",
            f"{self.imap_port}:3143",
            "-p",
            f"{self.pop3_port}:3110",
            "-p",
            f"{self.api_port}:8080",
            self.image,
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                print(f"Failed to start container: {result.stderr}")
            return result.returncode == 0
        except (subprocess.TimeoutExpired, Exception) as e:
            print(f"Exception starting container: {e}")
            return False

    def stop(self) -> bool:
        """
        Stop the GreenMail container.

        Returns:
            True if stopped successfully, False otherwise
        """
        import subprocess

        cmd = ["podman", "stop", self.container_name]

        try:
            subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            return True
        except (subprocess.TimeoutExpired, Exception):
            return False

    def is_running(self) -> bool:
        """
        Check if the GreenMail container is running.

        Returns:
            True if running, False otherwise
        """
        import subprocess

        cmd = ["podman", "ps", "--filter", f"name={self.container_name}", "--format", "{{.Names}}"]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            return self.container_name in result.stdout
        except (subprocess.TimeoutExpired, Exception):
            return False

    def wait_for_ready(self, timeout: int = 30) -> bool:
        """
        Wait for the GreenMail container to be ready.

        Args:
            timeout: Maximum time to wait in seconds (default: 30)

        Returns:
            True if ready, False if timeout
        """
        import socket
        import time

        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                # Try to connect to SMTP port
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                sock.connect(("localhost", self.smtp_port))
                sock.close()
                # Give GreenMail a bit more time to fully initialize after socket is ready
                time.sleep(2)
                return True
            except (socket.timeout, ConnectionRefusedError):
                time.sleep(1)

        return False
