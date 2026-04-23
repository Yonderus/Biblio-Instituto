from odoo import fields, models


class LibraryLoan(models.Model):
    _name = "library.loan"
    _description = "Prestamo de biblioteca"
    _order = "loan_date desc, id desc"

    
    copy_number = fields.Integer(required=True, default=1)
    loan_date = fields.Date(string="Fecha prestamo", default=fields.Date.context_today, required=True)
    expected_return_date = fields.Date(string="Fecha devolucion prevista", required=True)
    real_return_date = fields.Date(string="Fecha devolucion real")

    state = fields.Selection(
        selection=[
            ("activo", "Activo"),
            ("devuelto", "Devuelto"),
            ("vencido", "Vencido"),
        ],
        string="Estado prestamo",
        default="activo",
    )
    user_id = fields.Many2one("res.partner", required=True, ondelete="restrict")
    book_id = fields.Many2one("library.book", required=True, ondelete="restrict")