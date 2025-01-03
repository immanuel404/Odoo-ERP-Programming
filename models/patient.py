from odoo import api,fields,models,_
from odoo.exceptions import ValidationError


class HospitalPatient(models.Model):
  _name = "hospital.patient"
  _inherit = ['mail.thread']
  _description = "Patient Master"

  name = fields.Char(string="Name", required=True, tracking=True)
  date_of_birth = fields.Date(string="DOB", tracking=True)
  gender = fields.Selection(
    [
      ('male','Male'),
      ('female','Female'),
    ],string="Gender", tracking=True
  )
  patient_age = fields.Integer(string="Age", default=10)
  tag_ids = fields.Many2many('patient.tag', string="Tags")
  is_minor = fields.Boolean(string="Minor")
  guardian = fields.Char(string="Guardian")

  # on delete
  @api.ondelete(at_uninstall=False)
  def _check_patient_appointments(self):
    for rec in self:
      domain = [('patient_id','=',rec.id)]
      appointments = self.env['hospital.appointment'].search(domain)
      if appointments:
        raise ValidationError(_("You cannot delete the patient."))

  # alternate ondelete
  # def unlink(self):
  #   for rec in self:
  #     domain = [('patient_id','=',rec.id)]
  #     appointments = self.env['hospital.appointment'].search(domain)
  #     if appointments:
  #       raise ValidationError(_("You cannot delete the patient. Appointment(s) exist for %s" % rec.name))
  #   return super().unlink()