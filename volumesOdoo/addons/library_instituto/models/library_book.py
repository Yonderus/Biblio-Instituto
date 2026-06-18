from odoo import api, fields, models
from odoo.exceptions import ValidationError

class LibraryBook(models.Model):
    _name = "library.book"
    _description = "Libro de la biblioteca"
    _rec_name = "title"

    title = fields.Char("Título", required=True)
    isbn = fields.Char("ISBN-13", required=True)
    edition_year = fields.Integer("Año de edición")
    total_copies = fields.Integer("Número total de copias", default=1, required=True)

    genre = fields.Selection(
        selection=[
            ("narrativa", "Narrativa"),
            ("poesia", "Poesía"),
            ("teatro", "Teatro"),
            ("ensayo", "Ensayo"),
            ("divulgacion", "Divulgación"),
            ("comic", "Cómic"),
            ("libro_texto", "Libro de texto"),
            ("otro", "Otro"),
        ],
        string="Género",
        default="otro",
        required=True
    )

    state = fields.Selection(
        selection=[
            ("disponible", "Disponible"),
            ("prestado", "Prestado"),
            ("reparacion", "Reparación"),
            ("baja", "Baja"),
        ],
        string="Estado",
        default="disponible",
        required=True,
        compute="_compute_state",
        store=True,
        readonly=False,
    )

    cover_image = fields.Image("Portada", max_width=300, max_height=400)

    author_ids = fields.Many2many(
        "library.author",
        required=True)
    
    publisher_id = fields.Many2one(
        "library.publisher", 
        required=True, 
        ondelete="restrict")
    
    loan_ids = fields.One2many("library.loan", "book_id")

    active_loans_count = fields.Integer(
        "Préstamos activos",
        compute="_compute_available_copies",
        store=True
    )

    available_copies = fields.Integer(
        "Ejemplares disponibles",
        compute="_compute_available_copies",
        store=True,
    )

    # ============================================================================
    # CÁLCULOS AUTOMÁTICOS
    # ============================================================================

    @api.depends("total_copies", "loan_ids.state")
    def _compute_available_copies(self):
        # Cuenta préstamos activos o vencidos (excluye devueltos) y calcula ejemplares libres
        for book in self:
            prestamos_activos = len(book.loan_ids.filtered(lambda loan: loan.state in ["activo", "vencido"]))
            book.active_loans_count = prestamos_activos
            book.available_copies = max((book.total_copies or 0) - prestamos_activos, 0)

    # ============================================================================
    # VALIDACIONES
    # ============================================================================
    @api.depends("active_loans_count", "total_copies")
    def _compute_state(self):
        for book in self:
            if book.state not in ("reparacion", "baja"):
                if book.active_loans_count >= (book.total_copies or 1):
                    book.state = "prestado"
                else:
                    book.state = "disponible"

    def action_set_reparacion(self):
        for book in self:
            if book.active_loans_count > 0:
                raise ValidationError(
                    f'"{book.title}" tiene {book.active_loans_count} préstamo(s) activo(s). '
                    'Devuélvelos antes de ponerlo en reparación.'
                )
            book.state = "reparacion"

    def action_set_baja(self):
        for book in self:
            if book.active_loans_count > 0:
                raise ValidationError(
                    f'"{book.title}" tiene {book.active_loans_count} préstamo(s) activo(s). '
                    'Devuélvelos antes de darlo de baja.'
                )
            book.state = "baja"

    def action_reset_state(self):
        for book in self:
            if book.active_loans_count >= (book.total_copies or 1):
                book.state = "prestado"
            else:
                book.state = "disponible"

    _sql_constraints = [
        ('isbn_uniq', 'UNIQUE(isbn)', 'Ya hay un libro con ese ISBN.'),
    ]