import logging

from beanstream import billing, errors, transaction
from beanstream.response_codes import response_codes

log = logging.getLogger('beanstream.payment_profiles')


class PaymentProfileTransaction(transaction.Transaction):

    def __init__(self, beanstream):
        super(PaymentProfileTransaction, self).__init__(beanstream)
        self.url = self.URLS['payment_profile']
        self.response_class = PaymentProfileResponse

        if not self.beanstream.payment_profile_passcode:
            raise errors.ConfigurationException('payment profile passcode must be specified to create or modify payment profiles')

        self.params['serviceVersion'] = '1.0'
        self.params['merchantId'] = self.beanstream.merchant_id
        self.params['passCode'] = self.beanstream.payment_profile_passcode
        self.params['responseFormat'] = 'QS'

    def set_customer_code(self, customer_code):
        self.params['customerCode'] = customer_code

    def set_language(self, language):
        language = language.upper()
        if language not in ('ENG', 'FRE'):
            raise errors.ValidationException('invalid language option specified: %s (must be one of FRE, ENG)' % language)
        self.params['trnLanguage'] = language

    def set_velocity_id(self, velocity_id):
        self.params['velocityIdentity'] = velocity_id

    def set_status_id(self, status_id):
        self.params['statusIdentity'] = status_id

    def set_status(self, status):
        status = status.upper()
        if status not in 'ACD':
            raise errors.ValidationException('invalid status option specified: %s' % status)

        self.params['status'] = status


class CreatePaymentProfile(PaymentProfileTransaction):

    def __init__(self, beanstream, card):
        super(CreatePaymentProfile, self).__init__(beanstream)

        self.params['operationType'] = 'N'
        self.params.update(card.params())


class ModifyPaymentProfile(PaymentProfileTransaction):

    def __init__(self, beanstream, customer_code):
        super(ModifyPaymentProfile, self).__init__(beanstream)

        self.params['operationType'] = 'M'
        self.set_customer_code(customer_code)


class GetPaymentProfile(PaymentProfileTransaction):

    def __init__(self, beanstream, customer_code):
        super(GetPaymentProfile, self).__init__(beanstream)

        self.params['operationType'] = 'Q'
        self.set_customer_code(customer_code)


class PaymentProfileResponse(transaction.Response):

    def get_message(self):
        return self.resp.get('responseMessage', [None])[0]

    def customer_code(self):
        return self.resp.get('customerCode', [None])[0]

    def order_number(self):
        return self.resp.get('trnOrderNumber', [None])[0]

    def approved(self):
        return self.resp.get('responseCode', ['0'])[0] == '1'

    def get_message(self):
        return self.resp.get('responseMessage', ['0'])[0] == '1'

    def status(self):
        return self.resp.get('status', [None])[0]

    def billing_address(self):
        return billing.Address(
            self.resp.get('ordName', [None])[0],
            self.resp.get('ordEmailAddress', [None])[0],
            None, # no phone number, apparently
            self.resp.get('ordAddress1', [None])[0],
            self.resp.get('ordAddress2', [None])[0],
            self.resp.get('ordCity', [None])[0],
            self.resp.get('ordProvince', [None])[0],
            self.resp.get('ordPostalCode', [None])[0],
            self.resp.get('ordCountry', [None])[0],
        )

    def bank_account_type(self):
        return self.resp.get('bankAccountType', [None])[0]

    def card_number(self):
        return self.resp.get('trnCardNumber', [None])[0]

    def expiry(self):
        return self.resp.get('trnCardExpiry', [None])[0]

