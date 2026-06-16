from odoo import api, fields, models

class LibraryAuthor(models.Model):
    _name = 'library.author'
    _description = 'Autor del libro'

    name = fields.Char('Nombre', required=True)
    country_id = fields.Many2one('res.country', string='País')
    birth_date = fields.Date('Fecha de nacimiento')
    image = fields.Image('Foto', max_width=256, max_height=256)

    book_ids = fields.Many2many('library.book')
    book_count = fields.Integer('Nº de libros', compute='_compute_book_count', store=True)

    @api.depends('book_ids')
    def _compute_book_count(self):
        for author in self:
            author.book_count = len(author.book_ids)

    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Ya hay un autor con ese nombre.'),
    ]
    