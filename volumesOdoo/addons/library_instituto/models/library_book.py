from odoo import models, fields
from odoo.exceptions import ValidationError

class LibraryBook(models.Model):
    _name = "library.book"
    _description = "Libro de la biblioteca"
    _rec_name = "Titulo"  # Campo que se usará como nombre del registro

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
    ), 

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
    ), 

    cover_image = fields.Image("Portada", max_width=300, max_height=400) #La anchura y altura están ahora puestos a ojo

    author_id = fields.Many2one(
        comodel_name="library.author",
        string="Autor",
        required=True,
        ondelete="restrict",
    )
    publisher_id = fields.Many2one(
        comodel_name="library.publisher",
        string="Editorial",
        required=True,
        ondelete="restrict",
    )

    _sql_constraints = [
        ('isbn_uniq', 'UNIQUE(isbn)', 'Ya hay un libro con ese ISBN.'),
    ]