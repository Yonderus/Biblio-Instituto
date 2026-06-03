from odoo import api, fields, models
from odoo.exceptions import ValidationError


# _inherit amplía el modelo existente res.partner sin crear una tabla nueva
class ResPartner(models.Model):
    _inherit = "res.partner"

    library_course_group = fields.Char(string="Curso y grupo")
    library_card_number = fields.Char(string="Numero carnet biblioteca")
    library_max_loans = fields.Integer(string="Maximo prestamos simultaneos", default=3, required=True)
    library_active_loans = fields.Integer(
        string="Prestamos activos",
        compute="_compute_library_active_loans",
    )
    
    library_user_type = fields.Selection(
        selection=[
            ("alumno", "Alumno"),
            ("docente", "Docente"),
            ("administracion", "Personal de administracion"),
        ],
        string="Tipo de usuario biblioteca",
    )


    # ============================================================================
    # RELACIONES Y DATOS
    # ============================================================================
    _sql_constraints = [
        ("library_card_number_uniq", "UNIQUE(library_card_number)", "El numero de carnet ya existe."),
    ]

    library_loan_ids = fields.One2many("library.loan", "user_id")

    @api.depends("library_loan_ids.state")
    def _compute_library_active_loans(self):
        # Cuenta préstamos activos y vencidos del usuario (excluye devueltos)
        for partner in self:
            partner.library_active_loans = len(partner.library_loan_ids.filtered(lambda loan: loan.state in ["activo", "vencido"]))

    # ============================================================================
    # VALIDACIONES Y CONSTRAINTS
    # ============================================================================

    @api.constrains("library_max_loans", "library_loan_ids")
    def _check_library_max_loans(self):
        # Valida que el máximo no sea negativo y que los préstamos actuales no superen el límite
        active_states = ["activo", "vencido"]
        for partner in self:
            if partner.library_max_loans < 0:
                raise ValidationError("El máximo de préstamos no puede ser negativo.")

            active_loans = partner.library_loan_ids.filtered(lambda loan: loan.state in active_states)
            if len(active_loans) > partner.library_max_loans:
                raise ValidationError(
                    f'"{partner.display_name}" tiene más préstamos activos que el máximo permitido.'
                )
