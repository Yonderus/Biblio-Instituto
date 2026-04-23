from odoo import api, fields, models

class LibraryAuthor(models.Model):
    _name = 'library.author'
    _description = 'Autor del libro'

    name = fields.Char('Name', required=True)
    country = fields.Char('Pais de origen')
    born_date = fields.Date('Fecha de nacimiento')


    book_ids = fields.Many2many('library.book', 'author_id', string='Books')

    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Ya hay un autor con ese nombre.'),
    ]
    