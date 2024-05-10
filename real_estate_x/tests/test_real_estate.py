from odoo.tests import TransactionCase, SingleTransactionCase, Form
from odoo import Command, fields

GROUP_USER = 'real_estate_x.group_real_estate_manager'
GROUP_MANAGER = 'real_estate_x.group_real_estate_customer_rep'


class TestRealEstate(SingleTransactionCase):
    @classmethod
    def setUpClass(cls):
        print("---------setUpClass---------")
        super(TestRealEstate, cls).setUpClass()
        cls.manager_user = cls.env.ref(GROUP_MANAGER)
        cls.normal_user = cls.env.ref(GROUP_USER)
        cls.manager_user = cls.env.ref(GROUP_MANAGER)
        cls.user_manager = cls.env['res.users'].create({
            'name': 'Test Service Rep User',
            'login': 'portal_user',
            'password': 'portal_user',
            'email': 'portal_user@gladys.portal',
            'groups_id': [Command.set([cls.manager_user.id])],
        })
        Model = cls.env['problem.types']
        cls.question_problem = Model.create({
            'name': 'Test Problem Type',
            'is_question': True,
            'user_id': cls.user_manager.id,
        })
        cls.non_question_problem = Model.create({
            'name': 'Test Problem Not Question',
            'is_question': False,
            'user_id': cls.user_manager.id,
        })
        # Model =
        # cls.customer_rep = cls.env['customer.service'].create({
        #     'user_id': cls.user_manager.id,
        #     'sequence': 8,
        #     'problem_types_ids': [(6, 0, [cls.question_problem.id,
        #                                   cls.non_question_problem.id])]
        # })
        # print("----completed service ----%s", cls.customer_rep)

    def test_create_complaint(self):
        """Test function to create Compliant records."""
        print("---- Test Case Started ---")
        print("---- User Created ---%s", self.user_manager)
        # real_estate_form = Form(self.env['real.estate'])
        Model = self.env['real.estate']
        print("---- Test 1 Question Complaint ----")
        self._test_compliant_question(Model)
        print("---- Test 1 Completed ----")
        print("---- Test 2 Non Question Complaint ----")
        self._test_not_question_complaint(Model)
        print("---- Test 2 Completed ----")
        print("---- Test 3 Non Question with Intervention Complaint ----")
        self._test_3_non_question_complaint(Model)
        print("---- Test 3 Completed ----")
        print("---- Test 4 Complaint Drop Test ----")
        self._test_4_drop_complaint(Model)
        print("---- Test 4 Completed ----")
        print("---- Test Case Completed ---")

    def _test_4_drop_complaint(self, Model):
        self.real_estate_form = Model.create({
            'reporter_name': 'Test User',
            'reporter_email': 't@t.com',
            'reporter_phone': '1234567890',
            'reporter_address': 'Test Address',
            'description': 'Test Description',
            'problem_type_id': self.non_question_problem.id
        })
        self.assertEqual(self.real_estate_form.date,
                         fields.Date.today(), " Date Are Not Matching..")
        self.assertEqual(self.real_estate_form.service_rep_id.id,
                         self.user_manager.id, " Service Rep Assigning Failed")
        self._test_move_to_in_review()
        self._test_drop_complaint()
        # print("---------- _test_4_drop_complaint -------------")
        # print(self.real_estate_form.read())

    def _test_3_non_question_complaint(self, Model):
        self.real_estate_form = Model.create({
            'reporter_name': 'Test User',
            'reporter_email': 't@t.com',
            'reporter_phone': '1234567890',
            'reporter_address': 'Test Address',
            'description': 'Test Description',
            'problem_type_id': self.non_question_problem.id
        })
        self.assertEqual(self.real_estate_form.date,
                         fields.Date.today(), " Date Are Not Matching..")

        self.assertEqual(self.real_estate_form.service_rep_id.id,
                         self.user_manager.id, " Service Rep Assigning Faild")
        self._test_move_to_in_review()
        self.real_estate_form.write({'action_plan': 'Test Action Plan',
                                     'require_intervention': True})
        self._test_move_to_in_progress()
        report_action = self.real_estate_form.print_workorder()
        # print("Report Action",report_action)
        self.assertEqual(report_action['type'], 'ir.actions.report',
                         "Report Type Failed")
        self.assertEqual(report_action['report_type'], 'qweb-pdf',
                         "Report Type Failed")
        self._test_close_complaint()
        # print("--------- _test_3_non_question_complaint ----------")
        # print(self.real_estate_form.read())

    def _test_compliant_question(self, Model):
        self.real_estate_form = Model.create({
            'reporter_name': 'Test User',
            'reporter_email': 't@t.com',
            'reporter_phone': '1234567890',
            'reporter_address': 'Test Address',
            'description': 'Test Description',
            'problem_type_id': self.question_problem.id
        })
        self.assertEqual(self.real_estate_form.date,
                         fields.Date.today(), " Date Are Not Matching..")
        self.assertEqual(self.real_estate_form.service_rep_id.id,
                         self.user_manager.id, " Service Rep Assigning Faild")
        self._test_move_to_in_review()
        self.real_estate_form.answer_question = "Test Answer"
        self.real_estate_form.send_answer_to_question()
        self.assertEqual(self.real_estate_form.state,
                         'solved', "Status Change Failed")
        # print("------ _test_compliant_question -------------")
        # print(self.real_estate_form.read())
        # TODO:- Need to check mail send or not.

    def _test_not_question_complaint(self, Model):
        self.real_estate_form = Model.create({
            'reporter_name': 'Test User',
            'reporter_email': 't@t.com',
            'reporter_phone': '1234567890',
            'reporter_address': 'Test Address',
            'description': 'Test Description',
            'problem_type_id': self.non_question_problem.id
        })
        self.assertEqual(self.real_estate_form.date,
                         fields.Date.today(), " Date Are Not Matching..")
        self.assertEqual(self.real_estate_form.service_rep_id.id,
                         self.user_manager.id, " Service Rep Assigning Faild")
        self._test_move_to_in_review()
        self.real_estate_form.write({'action_plan': 'Test Action Plan',
                                     'require_intervention': False})
        self._test_move_to_in_progress()
        self._test_close_complaint()
        # print("---------------test_not_question_complaint --------------")
        # print(self.real_estate_form.read())

    def _test_move_to_in_review(self):
        self.real_estate_form.change_in_review()
        self.assertEqual(self.real_estate_form.state,
                         'in_review', "Status Change Failed")

    def _test_move_to_in_progress(self):
        self.real_estate_form.change_in_progress()
        self.assertEqual(self.real_estate_form.state,
                         'in_progress', "Status Change Failed")

    def _test_close_complaint(self):
        self.real_estate_form.close_complaint()
        self.assertEqual(self.real_estate_form.state,
                         'solved', "Status Change Failed")

    def _test_drop_complaint(self):
        self.real_estate_form.drop_reason = "Test Drop Reason"
        self.real_estate_form.drop_complaint()
        self.assertEqual(self.real_estate_form.state,
                         'dropped', "Status Change Failed")
