import premailer

from django.template.loader import render_to_string
from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six

def premailer_transform(html):
    p = premailer.Premailer(html)
    return p.transform()


def get_mail_body(mail_name, mail_params):
    response_html = premailer_transform(render_to_string("emails/" + mail_name + ".html", mail_params))
    return response_html


class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, delegate, timestamp):
        return (
            six.text_type(delegate.user.pk) + six.text_type(timestamp) +
            six.text_type(delegate.user.is_active)
        )

account_activation_token = TokenGenerator()
