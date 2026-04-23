from odoo import fields, models

class LibraryAuthor(models.Model):
    _name = 'library.author'
    _description = 'Autor del libro'

    name = fields.Char('Name', required=True)
    pais = fields.Char('Pais de origen')
    fecha_nacimiento = fields.Date('Fecha de nacimiento')


    book_ids = fields.Many2many('library.book')

    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Ya hay un autor con ese nombre.'),
    ]
    