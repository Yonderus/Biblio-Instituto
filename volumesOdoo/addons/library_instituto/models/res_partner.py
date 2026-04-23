from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    library_course_group = fields.Char(string="Curso y grupo")
    library_card_number = fields.Char(string="Numero carnet biblioteca")
    library_max_loans = fields.Integer(string="Maximo prestamos simultaneos", default=3, required=True)
    library_active_loans = fields.Integer(string="Prestamos activos", default=0)
    
    library_user_type = fields.Selection(
        selection=[
            ("alumno", "Alumno"),
            ("docente", "Docente"),
            ("administracion", "Personal de administracion"),
        ],
        string="Tipo de usuario biblioteca",
    )

    _sql_constraints = [
        ("library_card_number_uniq", "UNIQUE(library_card_number)", "El numero de carnet ya existe."),
    ]

    library_loan_ids = fields.One2many("library.loan", "user_id")
