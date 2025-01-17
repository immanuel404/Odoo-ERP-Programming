from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class DynamicField(models.Model):
  _name = 'dynamic.field'
  _description = 'Dynamic Field'
  _inherit = ['mail.thread']

  field_name = fields.Char(string='Field Name', required=True)
  field_type = fields.Selection([
    ('char', 'Char'),
    ('text', 'Text'),
    ('integer', 'Integer'),
    ('float', 'Float'),
    ('boolean', 'Boolean'),
    ('date', 'Date'),
    ('datetime', 'Datetime'),
    ('many2one', 'Many2One'),
    ('many2many', 'Many2Many'),
    ('one2many', 'One2Many'),
  ], string='Field Type', required=True)
  related_model = fields.Char(string='Related Model', default='mun.meter', required=True)


  def create(self, vals):
    field_name = vals.get('field_name')
    field_type = vals.get('field_type')
    related_model = vals.get('related_model', 'mun.meter')

    # Validate field name
    if not field_name or not field_name.isidentifier():
      raise ValidationError(_("Field name must be a valid identifier."))

    # Check if field already exists
    if self.env['ir.model.fields'].search([
      ('name', '=', field_name),
      ('model', '=', related_model)
    ]):
      raise ValidationError(_("Field '%s' already exists in model '%s'.") % (field_name, related_model))

    # Map Odoo field types
    field_type_map = {
      'char': 'char', 'text': 'text', 'integer': 'integer', 'float': 'float',
      'boolean': 'boolean', 'date': 'date', 'datetime': 'datetime',
      'many2one': 'many2one', 'many2many': 'many2many', 'one2many': 'one2many',
    }
    if field_type not in field_type_map:
      raise ValidationError(_("Invalid field type '%s'.") % field_type)

    # Create field in ir.model.fields
    model = self.env['ir.model'].search([('model', '=', related_model)], limit=1)
    if not model:
      raise ValidationError(_("Model '%s' does not exist.") % related_model)

    self.env['ir.model.fields'].create({
      'name': field_name,
      'model_id': model.id,
      'field_description': field_name.replace('_', ' ').capitalize(),
      'ttype': field_type_map[field_type],
      'state': 'manual',
    })

    # Create an inherited view to add the dynamic field
    self.create_inherited_view(related_model, field_name)
    return super(DynamicField, self).create(vals)


  def create_inherited_view(self, related_model, field_name):
    view = self.env['ir.ui.view'].search([
      ('model', '=', related_model),
      ('type', '=', 'form')
    ], limit=1)
    if not view:
      raise ValidationError(_("No form view found for model '%s'.") % related_model)

    # Create or update the inherited view
    self.env['ir.ui.view'].create({
      'name': f"Inherited view for {related_model} - {field_name}",
      'type': 'form',
      'model': related_model,
      'inherit_id': view.id,
      'arch_base': f"""
        <data>
          <xpath expr="//sheet" position="inside">
            <group>
                <field name="{field_name}"/>
            </group>
          </xpath>
        </data>
      """
    })