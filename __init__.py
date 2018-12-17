# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from . import contract

def register():
    Pool.register(
        contract.ContractLine,
        contract.ApplyDiscountStart,
        module='contract_apply_discount', type_='model')
    Pool.register(
        contract.ApplyDiscount,
        module='contract_apply_discount', type_='wizard')
