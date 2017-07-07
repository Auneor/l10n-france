# -*- coding: utf-8 -*-
# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# Copyright (C) 2017 - Today: Akretion (http://www.akretion.com)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api
from openerp.tools.config import config


class PosConfig(models.Model):
    _name = 'pos.config'
    _inherit = ['pos.config', 'certification.sequence.holder.mixin']

    _secured_model_name = 'pos.order'

    _SELECTION_PREVENT_PRINT_LEGACY = [
        ('no', 'Allow Printing'),
        ('warning', 'Mark a Warning'),
        ('block', 'Prevent Printing'),
    ]

    l10n_fr_prevent_print = fields.Char(
        string='Prevent Uncertified Bill (Computed)',
        compute='_compute_l10n_fr_prevent_print',
        help="Indicate what is the behaviour of the Point of Sale, if"
        " the server is unreachable\n"
        "This field is a computed field, based on 'Prevent Uncertified Bill'"
        " and the value of the key 'l10n_fr_certification_mode' in the server"
        " configuration file.")

    l10n_fr_prevent_print_legacy = fields.Selection(
        string='Prevent Uncertified Bill', default='no',
        selection=_SELECTION_PREVENT_PRINT_LEGACY, help="Indicate what is the"
        " behaviour of the Point of Sale, if the server is unreachable\n"
        " * 'Allow Printing': Normal behaviour\n"
        " * 'Mark a Warning': A warning text will be printed on the bill\n"
        " * 'Prevent Printing': The downgraded mode is disabled and the"
        " cashier will not have the possibility to give the bill to the"
        " customer, if there is a network problem. This is the most secure"
        " mode from a point of view of certification but you have to ensure"
        " that network connection is reliable.\n\n"
        " Note : This setting has no effect, if server configuration file"
        " has a value different to 'legacy', for the key"
        " 'l10n_fr_certification_mode'")

    @api.multi
    def _get_certification_country(self):
        self.ensure_one()
        return self.company_id.country_id

    @api.multi
    def _get_certification_company(self):
        self.ensure_one()
        return self.company_id

    @api.multi
    def write(self, vals):
        res = super(PosConfig, self).write(vals)
        # Note: this part of code should be set in the module
        # l10n_fr_certification_abstract, but overloading write function
        # doesn't work for AbstractModel. (even if it works for create
        # function)
        self.generate_secure_sequence_if_required()
        return res

    # Compute Section
    @api.multi
    def _compute_l10n_fr_prevent_print(self):
        file_value = config.get('l10n_fr_certification_mode', 'legacy')
        for pos_config in self:
            if file_value == 'legacy':
                pos_config.l10n_fr_prevent_print =\
                    pos_config.l10n_fr_prevent_print_legacy
            else:
                pos_config.l10n_fr_prevent_print = file_value
