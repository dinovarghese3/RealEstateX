from odoo import models, fields, api, _


class RealEstate(models.Model):
    _name = 'real.estate'
    _description = 'RealEstate'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _rec_name = 'order_no'
    _order = 'id desc'

    """
    Workflow:-
    New --> In Review --> In Progress --> Solved --> Dropped.
    ---> Complaint Created.
    ---> Problem Type -> is a Question -> Service Rep can Able Answer the 
    Question and close the case.
    ---> Problem Type --> is not a Question --> Service Rep can change the 
    state.
    to in review add the action plan -> In progress -> solve.
    ---> Need Intervention -> Print the Work Order.
    ---> Drop -> Enter the drop reason and drop the complaint. 
    
    """

    def _get_domain(self):
        """Customer Service Rep Domain."""
        user_ids = self.env.ref(
            'real_estate_x.group_real_estate_customer_rep').users - self.env.ref(
            'real_estate_x.group_real_estate_manager').users
        return [('id', 'in', user_ids.ids)]

    active = fields.Boolean(default=True)
    order_no = fields.Char(string="Order No", default=lambda self: _('New'))
    reporter_name = fields.Char(string="Reporter Name", required=True)
    reporter_email = fields.Char(string="Reporter Email", required=True)
    reporter_phone = fields.Char(string="Reporter Phone")
    reporter_address = fields.Text(string="Reporter Address", required=True)
    problem_type_id = fields.Many2one('problem.types', string="Type")
    description = fields.Text(string="Description")
    date = fields.Date(string="Date", default=fields.Date.today())
    state = fields.Selection([('new', 'New'), ('in_review', 'In Review'),
                              ('in_progress', 'In Progress'),
                              ('solved', 'Solved'), ('dropped', 'Dropped')],
                             default='new', string="State",
                             track_visibility='onchange')

    service_rep_id = fields.Many2one('res.users', string="Customer Service "
                                                         "Rep",
                                     track_visibility='onchange',domain=_get_domain)
    action_plan = fields.Text(string="Action Plan", track_visibility='onchange')
    company_id = fields.Many2one('res.company', string="Company",
                                 default=lambda self: self.env.user.company_id)

    answer_question = fields.Text(string="Answer TO Question",
                                  track_visibility='onchange', help="Enter your"
                                                                    "Answer to the Question.")
    drop_reason = fields.Text(string="Drop Reason",
                              track_visibility='onchange', help="Reason for "
                                                                "Dropping the Complaint")
    drop_reason_id = fields.Many2one('drop.reasons', string="Dropping Reason",
                                     track_visibility='onchange')

    require_intervention = fields.Boolean(string="Require Intervention",
                                          default=False, help="If need any "
                                                              "intervention.",
                                          track_visibility='onchange')

    is_question_type = fields.Boolean(string="Is Question",
                                      related="problem_type_id.is_question")
    internal_note = fields.Text(string="Internal Note", help="Internal Notes",
                                track_visibility='onchange')
    resolution_note = fields.Text(string="Resolution Note",
                                  help="Resolution Notes this will send with the"
                                       "compliant close mail",
                                  track_visibility='onchange')

    @api.constrains('reporter_email')
    def send_register_mail(self):
        """
        Send the Complaint Register Mail.
        """
        mail_template = self.env.ref(
            'real_estate_x.complaint_real_Estate_template').sudo()
        mail_template.send_mail(self.id, force_send=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'order_no' not in vals or vals.get('order_no') == _('New'):
                vals['order_no'] = self.env['ir.sequence'].next_by_code(
                    'real.estate') or _('New')
        return super().create(vals_list)

    @api.constrains('problem_type_id', 'order_no')
    def assign_customer_service_rep(self):
        """
        Assign customer service rep.
        CurrentFlow:- Currently selecting the first user based on the problem type.
        The mail will send to the Service Rep
        """
        if self.problem_type_id and self.problem_type_id.user_id and not self.service_rep_id:
            self.write({'service_rep_id': self.problem_type_id.user_id.id})
            template = self.env.ref(
                'real_estate_x.assigned_real_Estate_template')
            template.send_mail(self.id, force_send=True)

    def print_workorder(self):
        """
        Function to print the work order pdf.
        """
        return self.env.ref(
            'real_estate_x.action_report_work_order').report_action(self.id)

    def drop_complaint(self):
        """Change the Complaint state to Dropped."""
        self.state = 'dropped'

    def close_complaint(self):
        """Function to close the Complaint.
        - if the problem is a question the service rep can enter the answer
        to question the answer will send throw mail to the reporter"""
        if self.problem_type_id.is_question:
            return {
                'name': _('Answer To Question'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'real.estate',
                'res_id': self.id,
                'target': 'new',
                'view_id': self.env.ref(
                    'real_estate_x.real_estate_answer_form_view').id,

            }
        mail_template = self.env.ref(
            'real_estate_x.complaint_solve_real_estate')
        mail_template.send_mail(self.id, force_send=True)
        self.state = 'solved'


    def drop_complaint_wizard(self):
        """Function to open the Dropping Reason Wizard"""
        return {
            'name': _('Drop Reason'),
            'view_mode': 'form',
            'res_model': 'real.estate',
            'res_id': self.id,
            'target': 'new',
            'view_id': self.env.ref(
                'real_estate_x.real_estate_drop_form_view').id,
            'type': 'ir.actions.act_window',
        }

    def send_answer_to_question(self):
        """If the Problem is a question. Then the Service Rep can just enter
        the answer and send it throw mail.The Complaint will be solved."""
        mail_template = self.env.ref(
            'real_estate_x.answer_real_Estate_template')
        mail_template.send_mail(self.id, force_send=True)
        self.write({'state': 'solved'})

    def change_in_review(self):
        """Change the Complaint state to in review."""
        self.write({'state': 'in_review'})

    def change_in_progress(self):
        """Change the Complaint state to in progress."""
        self.write({'state': 'in_progress'})
