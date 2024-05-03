from odoo import http
from odoo.http import request


class WebsiteForm(http.Controller):
    @http.route(['/support_real_estate'], type='http', auth="public",
                website=True)
    def support_real_estate(self):
        problem_types = (request.env['problem.types'].sudo().
                         search_read([], fields=['id', 'name']))

        return request.render("real_estate_x.support_real_estate_template",
                              {'problem_types': problem_types})

    @http.route(['/submit_support_form'], type='http', auth="public",
                website=True, )
    def submit_support_from(self, **kw):
        support = request.env['real.estate'].sudo().create({
            'reporter_name': kw.get('reporter_name'),
            'reporter_email': kw.get('reporter_email'),
            'reporter_phone': kw.get('reporter_phone'),
            'reporter_address': kw.get('reporter_address'),
            'description': kw.get('description'),
            'problem_type_id': int(kw.get('problem_type_id')),
        })
        return request.render("real_estate_x.support_feedback_template",
                              {'order_no': support.sudo().order_no})
