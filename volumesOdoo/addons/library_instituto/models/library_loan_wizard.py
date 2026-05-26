from datetime import timedelta
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class LibraryLoanWizard(models.TransientModel):
    """
    Wizard (asistente emergente) para crear varios préstamos a la vez.
    TransientModel: los datos se guardan temporalmente en BD y Odoo los borra solos.
    """
    _name = "library.loan.wizard"
    _description = "Asistente de préstamos múltiples"

    # Usuario al que se le hacen todos los préstamos del wizard
    user_id = fields.Many2one("res.partner", string="Usuario", required=True)

    # Líneas: cada una representa un libro a prestar
    line_ids = fields.One2many("library.loan.wizard.line", "wizard_id", string="Libros")

    def action_confirm(self):
        """
        Se ejecuta al pulsar "Confirmar préstamos".
        Recorre cada línea y crea un library.loan por cada una.
        Reutiliza la misma lógica de validación que ya tiene library.loan.
        """
        if not self.line_ids:
            raise ValidationError("Añade al menos un libro antes de confirmar.")

        today = fields.Date.context_today(self)
        for line in self.line_ids:
            self.env["library.loan"].create({
                "user_id": self.user_id.id,
                "book_id": line.book_id.id,
                "copy_number": line.copy_number,
                "loan_date": today,
                "expected_return_date": today + timedelta(days=15),
            })


class LibraryLoanWizardLine(models.TransientModel):
    """
    Línea del wizard: representa un libro concreto dentro del préstamo múltiple.
    """
    _name = "library.loan.wizard.line"
    _description = "Línea del asistente de préstamos"

    # Relación con la cabecera del wizard
    wizard_id = fields.Many2one("library.loan.wizard", required=True, ondelete="cascade")

    # Libro a prestar
    book_id = fields.Many2one("library.book", string="Libro", required=True)

    # Número de ejemplar físico
    copy_number = fields.Integer(string="Nº ejemplar", default=1)
