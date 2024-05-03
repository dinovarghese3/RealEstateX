from odoo import api, fields, models


class RealEstate(models.Model):
    _name = 'problem.types'
    _description = 'Problem Types'

    def _get_domain(self):
        """Customer Service Rep Domain."""
        user_ids = self.env.ref(
            'real_estate_x.group_real_estate_customer_rep').users - self.env.ref(
            'real_estate_x.group_real_estate_manager').users
        return [('id', 'in', user_ids.ids)]


    name = fields.Char(string="Name", required=True)
    is_question = fields.Boolean(string="Is Question", default=False)
    user_id = fields.Many2one('res.users', string="User", help="Select User",
                              domain=_get_domain)
    company_id = fields.Many2one('res.company', string="Company",
                                 default=lambda self: self.env.user.company_id)


class DropReason(models.Model):
    _name = 'drop.reasons'
    _description = 'Drop Reasons'

    name = fields.Char(string="Name", required=True)
    company_id = fields.Many2one('res.company', string="Company",
                                 default=lambda self: self.env.user.company_id)


