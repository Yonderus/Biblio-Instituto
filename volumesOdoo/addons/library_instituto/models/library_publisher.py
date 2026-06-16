from odoo import api, fields, models

class LibraryPublisher(models.Model):
    _name = "library.publisher"
    _description = "Editorial del libro"

    name = fields.Char('Nombre', required=True)
    city = fields.Char('Ciudad')
    country_id = fields.Many2one('res.country', string='País')
    email = fields.Char('Email')
    phone = fields.Char('Telefono', required=True)

    book_ids = fields.One2many('library.book', 'publisher_id')
    book_count = fields.Integer('Nº de libros', compute='_compute_book_count', store=True)

    @api.depends('book_ids')
    def _compute_book_count(self):
        for publisher in self:
            publisher.book_count = len(publisher.book_ids)

    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Ya hay una editorial con ese nombre.'),
    ]