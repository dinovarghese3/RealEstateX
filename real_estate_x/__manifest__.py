{
    'name': 'RealEstateX',
    'version': '17.0.1.0.1',
    'depends': ['base', 'website','mail'],
    'author': "Dino Varghese",
    'category': 'Real Estate',
    'summary': """Module is used to manage the complaints and
    Questions related to the real estate.""",
    'description': """The users can create their complaint requests on the website. The complaints will be sent to the real estate.""",
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'data/problem_type.xml',
        'data/drop_reason_data.xml',
        'views/problem_types_view.xml',
        'views/real_restate_views.xml',
        'views/support_real_estate_template.xml',
        'report/work_order.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
}
