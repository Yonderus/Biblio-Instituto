from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    """
    Extensión del modelo res.partner (Contactos) con campos y lógica específica de biblioteca.
    Representa usuarios de la biblioteca: alumnos, docentes, personal administrativo.
    """
    _inherit = "res.partner"

    # ============================================================================
    # CAMPOS DE USUARIO BIBLIOTECA
    # ============================================================================
    library_course_group = fields.Char(
        string="Curso y grupo",
        help="Solo para alumnos. Ej: '1A', '2B', '3C'. Sirve para identificar el grupo."
    )
    
    library_card_number = fields.Char(
        string="Numero carnet biblioteca",
        help="ID único del carnet de biblioteca (UNIQUE). Ej: 'BIB001'. "
             "Se usa para identificar rápidamente al usuario."
    )
    
    library_max_loans = fields.Integer(
        string="Maximo prestamos simultaneos", 
        default=3, 
        required=True,
        help="Número máximo de libros que este usuario puede tener en préstamo al mismo tiempo. "
             "El constraint _check_loan_limit valida que no se exceda esta cantidad."
    )
    
    library_active_loans = fields.Integer(
        string="Prestamos activos",
        compute="_compute_library_active_loans",
        help="Contador de préstamos actuales en estados 'activo' o 'vencido' (readonly, calculado)."
    )
    
    library_user_type = fields.Selection(
        selection=[
            ("alumno", "Alumno"),
            ("docente", "Docente"),
            ("administracion", "Personal de administracion"),
        ],
        string="Tipo de usuario biblioteca",
        help="Categoría del usuario. Determina permisos y límites de préstamos. "
             "Alumnos: máx 2-3, Docentes: máx 4, Admin: máx 5."
    )


    # ============================================================================
    # RELACIONES Y DATOS
    # ============================================================================
    _sql_constraints = [
        ("library_card_number_uniq", "UNIQUE(library_card_number)", "El numero de carnet ya existe."),
    ]

    library_loan_ids = fields.One2many(
        "library.loan", 
        "user_id",
        help="Historial completo de préstamos del usuario (activos, vencidos, devueltos)."
    )

    # ============================================================================
    # CÁLCULOS AUTOMÁTICOS
    # ============================================================================

    @api.depends("library_loan_ids.state")
    def _compute_library_active_loans(self):
        """
        Cuenta el número de préstamos "activos" o "vencidos" que tiene el usuario EN ESTE MOMENTO.
        
        Se recalcula automáticamente cuando:
        - Se crea un nuevo préstamo
        - Se devuelve un libro (estado → devuelto)
        - El sistema detecta que pasó la fecha de devolución (estado → vencido)
        
        Uso:
        - Se muestra en el formulario del usuario como info readonly.
        - Ayuda al personal de biblioteca a ver de un vistazo cuántos libros tiene activos.
        
        Ejemplo:
        - Laura tiene 2 préstamos: 1 activo + 1 vencido → library_active_loans = 2
        - Devuelve el libro vencido → library_active_loans = 1
        """
        for partner in self:
            partner.library_active_loans = len(partner.library_loan_ids.filtered(lambda loan: loan.state in ["activo", "vencido"]))

    # ============================================================================
    # VALIDACIONES Y CONSTRAINTS
    # ============================================================================

    @api.constrains("library_max_loans", "library_loan_ids")
    def _check_library_max_loans(self):
        """
        Validación de integridad de datos del lado de la BD.
        Se ejecuta automáticamente al cambiar library_max_loans o library_loan_ids.
        
        Dos validaciones:
        1. library_max_loans no puede ser negativo (previene números ilógicos).
        2. Los préstamos actuales activos/vencidos no pueden exceder el máximo permitido.
        
        Nota: El constraint REAL que impide nuevos préstamos está en library_loan._check_loan_limit.
        Este constraint es de "limpieza" en caso de cambios posteriores en max_loans o migraciones.
        
        Ejemplo:
        - Carlos (docente) tiene max 4 préstamos.
        - Tiene 3 activos. Admin lo intenta cambiar a max 2 → ERROR.
        """
        active_states = ["activo", "vencido"]
        for partner in self:
            if partner.library_max_loans < 0:
                raise ValidationError("El máximo de préstamos no puede ser negativo.")

            active_loans = partner.library_loan_ids.filtered(lambda loan: loan.state in active_states)
            if len(active_loans) > partner.library_max_loans:
                raise ValidationError(
                    f'"{partner.display_name}" tiene más préstamos activos que el máximo permitido.'
                )
