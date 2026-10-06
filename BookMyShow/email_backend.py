import smtplib

from django.core.mail.backends.smtp import EmailBackend


class CustomEmailBackend(EmailBackend):

    def open(self):
        if self.connection:
            return False

        try:
            self.connection = smtplib.SMTP(
                self.host,
                self.port,
                timeout=self.timeout
            )

            if self.use_tls:
                self.connection.starttls()

            if self.username and self.password:
                self.connection.login(
                    self.username,
                    self.password
                )

            return True

        except OSError:
            if not self.fail_silently:
                raise

            return False