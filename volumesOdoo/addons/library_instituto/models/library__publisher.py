from odoo import models, fields

class LibraryPublisher(models.Model):
    _name = "library.publisher"
    _description = "Editorial del libro"

    name = fields.Char('Name', required=True)
    city = fields.Char('Ciudad')
    email = fields.Char('Email')
    phone = fields.Char('Telefono', required=True)
    
    book_ids = fields.One2many('library.book', 'publisher_id', string='Books')

    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Ya hay una editorial con ese nombre.'),
    ]