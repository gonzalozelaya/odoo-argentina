from odoo import models, fields, api
import logging

_logger= logging.getLogger(__name__)

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_id')
    def on_change_tax(self):
        for line in self:
            _logger.info('on change sale order line')
            
            # Asegúrate de que partner_id y perceptions estén disponibles
            partner = line.order_id.partner_id
            if partner:
                impuestos = partner.perceptions
                # Combinar impuestos existentes con los nuevos
                impuestos_agregar = line.tax_id | impuestos
                # Asignar directamente
                line.tax_id = [(6, 0, impuestos_agregar.ids)]
            else:
                _logger.warning('El campo order_id.partner_id está vacío o perceptions no está definido.')
