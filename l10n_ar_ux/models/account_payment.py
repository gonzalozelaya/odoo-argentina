from odoo import fields, models, api


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    l10n_ar_partner_vat = fields.Char(related='partner_id.l10n_ar_vat', string='CUIT del destinatario')

    @api.model
    def _get_trigger_fields_to_sincronize(self):
        res = super()._get_trigger_fields_to_sincronize()
        return res + ('l10n_latam_check_payment_date',)

    def _prepare_move_line_default_vals(self, write_off_line_vals=None):
        """ Add check name and operation on liquidity line """
        res = super()._prepare_move_line_default_vals(write_off_line_vals=write_off_line_vals)
        date_maturity = False
        check = self if self.payment_method_line_id.code == 'new_third_party_checks' else self.l10n_latam_check_id
        if check:
            date_maturity = check.l10n_latam_check_payment_date
        elif self.payment_method_line_id.code == 'check_printing' and self.l10n_latam_check_payment_date:
            date_maturity = self.l10n_latam_check_payment_date
        if date_maturity:
            for vals in res:
                vals.update({
                    'date_maturity': date_maturity,
                })
        return res

    @api.depends('payment_method_code', 'l10n_latam_check_id', 'check_number')
    def _compute_payment_method_description(self):
        check_payments = self.filtered(
            lambda x: x.payment_method_code in ['check_printing', 'new_third_party_checks', 'out_third_party_checks', 'in_third_party_checks'])
        for rec in check_payments:
            if rec.l10n_latam_check_id:
                checks_desc = rec.l10n_latam_check_id.check_number
            else:
                checks_desc = rec.check_number or ''
            name = "%s: %s" % (rec.payment_method_line_id.display_name, checks_desc)
            rec.payment_method_description = name
        return super(AccountPayment, (self - check_payments))._compute_payment_method_description()
