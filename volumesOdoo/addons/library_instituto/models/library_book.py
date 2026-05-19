from odoo import api, fields, models

class LibraryBook(models.Model):
    """
    Modelo de Libros de la biblioteca.
    Gestiona el catálogo de libros: metadatos, disponibilidad y relaciones con autores/editoriales.
    """
    _name = "library.book"
    _description = "Libro de la biblioteca"
    _rec_name = "title"

    title = fields.Char("Titulo", required=True)
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
        required=True
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
        """
        Calcula el número de ejemplares disponibles en TIEMPO REAL.
        
        Fórmula:
        available_copies = total_copies - (préstamos activos + préstamos vencidos)
        
        Detalles:
        - Cuenta solo préstamos en "activo" o "vencido" (excluye "devuelto").
        - Se actualiza automáticamente cuando:
          * Se crea un nuevo préstamo
          * Se devuelve un libro (estado → devuelto)
          * Se renueva un préstamo
        
        Ejemplos:
        1. Libro con 3 copias, 2 préstamos activos → available_copies = 1
        2. Mismo libro, se devuelven todos → available_copies = 3
        3. Mismo libro, 1 activo + 1 vencido → available_copies = 1
        
        Uso en UI:
        - Se muestra en la lista de libros y en el kanban como "Disponibles: X".
        - En kanban aparece un badge azul con esta cantidad.
        - Ayuda a usuarios a ver si pueden prestar el libro.
        """
        for book in self:
            active_loans = len(book.loan_ids.filtered(lambda loan: loan.state in ["activo", "vencido"]))
            book.available_copies = max((book.total_copies or 0) - active_loans, 0)

    # ============================================================================
    # VALIDACIONES
    # ============================================================================
    _sql_constraints = [
        ('isbn_uniq', 'UNIQUE(isbn)', 'Ya hay un libro con ese ISBN.'),
    ]