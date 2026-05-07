from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class LibraryLoan(models.Model):
    _name = "library.loan"
    _description = "Prestamo de biblioteca"
    _order = "loan_date desc, id desc"

    
    copy_number = fields.Integer(required=True, default=1)
    loan_date = fields.Date(string="Fecha prestamo", default=fields.Date.context_today, required=True)
    expected_return_date = fields.Date(string="Fecha devolucion prevista", required=True)
    real_return_date = fields.Date(string="Fecha devolucion real")
    
    late_days = fields.Integer(
        string="Dias de retraso",
        compute="_compute_late_days",
        store=True,
    )
    renewed = fields.Boolean(string="Renovado", default=False)

    state = fields.Selection(
        selection=[
            ("activo", "Activo"),
            ("devuelto", "Devuelto"),
            ("vencido", "Vencido"),
        ],
        string="Estado prestamo",
        compute="_compute_state",
        store=True,
    )
    user_id = fields.Many2one("res.partner", required=True, ondelete="restrict")
    book_id = fields.Many2one("library.book", required=True, ondelete="restrict")

    @api.onchange("loan_date")
    def _onchange_loan_date(self):
        if self.loan_date:
            self.expected_return_date = self.loan_date + timedelta(days=15)

    @api.depends("real_return_date", "expected_return_date")
    def _compute_state(self):
        today = fields.Date.context_today(self)
        for loan in self:
            if loan.real_return_date:
                loan.state = "devuelto"
            elif loan.expected_return_date and loan.expected_return_date < today:
                loan.state = "vencido"
            else:
                loan.state = "activo"

    @api.depends("state", "expected_return_date", "real_return_date")
    def _compute_late_days(self):
        today = fields.Date.context_today(self)
        for loan in self:
            if loan.state == "devuelto" and loan.real_return_date and loan.expected_return_date:
                loan.late_days = max((loan.real_return_date - loan.expected_return_date).days, 0)
            elif loan.state == "vencido" and loan.expected_return_date:
                loan.late_days = max((today - loan.expected_return_date).days, 0)
            else:
                loan.late_days = 0

    @api.constrains("copy_number")
    def _check_copy_number(self):
        for loan in self:
            if loan.copy_number < 1:
                raise ValidationError("El numero de ejemplar debe ser mayor o igual a 1.")

    def action_return(self):
        for loan in self:
            if loan.state != "devuelto":
                loan.real_return_date = fields.Date.context_today(self)

    def action_renew(self):
        for loan in self:
            if loan.state not in ["activo", "vencido"]:
                raise ValidationError("Solo puedes renovar prestamos activos o vencidos.")
            if loan.renewed:
                raise ValidationError("Este prestamo ya fue renovado una vez.")
            if not loan.expected_return_date:
                raise ValidationError("El prestamo no tiene fecha de devolucion prevista.")
            loan.expected_return_date = loan.expected_return_date + timedelta(days=15)
            loan.renewed = True