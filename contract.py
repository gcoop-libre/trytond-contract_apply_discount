# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from decimal import Decimal, ROUND_HALF_UP

from trytond.model import ModelView, fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval
from trytond.wizard import Button, StateTransition, StateView, Wizard
from trytond.modules.product.product import price_digits

__all__ = ['ContractLine', 'ApplyDiscountStart', 'ApplyDiscount']


class ContractLine:
    __name__ = 'contract.line'
    __metaclass__ = PoolMeta

    @classmethod
    def apply_discount_by_percentage(cls, lines, percentage):
        for line in lines:
            line.discount = Decimal(str(percentage))
            line.on_change_discount()
            line.save()


class ApplyDiscountStart(ModelView):
    'Apply Discount - Start'
    __name__ = 'contract.apply_discount.start'

    date = fields.Date('Start period date', required=True)
    method = fields.Selection([
            ('percentage', 'By Percentage'),
            ], 'Apply Discount method', required=True)
    percentage = fields.Float('Percentage', digits=(16, 4),
        states={
            'invisible': Eval('method') != 'percentage',
            'required': Eval('method') == 'percentage',
            },
        depends=['method'])
    categories = fields.Many2Many('product.category', None, None, 'Categories',
        states={
            'invisible': Eval('method') != 'percentage',
            'required': Eval('method') == 'percentage',
            }, depends=['method'])



class ApplyDiscount(Wizard):
    'Apply Discount'
    __name__ = 'contract.apply_discount'

    start = StateView('contract.apply_discount.start',
        'contract_apply_discount.apply_discount_start_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Apply', 'apply_discount', 'tryton-ok', default=True),
            ])
    apply_discount = StateTransition()

    def get_additional_args(self):
        method_name = 'get_additional_args_%s' % self.start.method
        if not hasattr(self, method_name):
            return {}
        return getattr(self, method_name)()

    def get_additional_args_percentage(self):
        return {
            'percentage': self.start.percentage,
            }

    def transition_apply_discount(self):
        pool = Pool()
        ContractLine = pool.get('contract.line')

        method_name = 'apply_discount_by_%s' % self.start.method
        method = getattr(ContractLine, method_name)
        if method:
            domain = [
                ('contract_state', '=', 'confirmed'),
                ('contract.start_period_date', '<=', self.start.date),
                ]
            if self.start.categories:
                categories = [cat.id for cat in list(self.start.categories)]
                domain.append(('service.product.categories', 'in', categories))
            method(ContractLine.search(domain),
                **self.get_additional_args())
        return 'end'
