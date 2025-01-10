from odoo import api,fields,models


class HospitalAppointment(models.Model):
  _name = "hospital.appointment"
  _inherit = ['mail.thread']
  _description = "Appointment Master"
  _rec_names_search = ['reference','patient_id'] # search multiple fields in the many2one search filter (use ref to find..)
  _rec_name = "patient_id"

  reference = fields.Char(string="Reference", default="New")
  patient_id = fields.Many2one('hospital.patient', string="Patient", ondelete="restrict") # ondelete="cascade"
  date_appointment = fields.Date(string="Date")
  note = fields.Text(string="Note")
  state = fields.Selection([
    ("draft","Draft"),("confirmed","Confirmed"),("ongoing","Ongoing"),
    ("done","Done"),("cancel","Cancelled")
  ], default='draft', tracking=True)
  appointment_line_ids = fields.One2many(
    'hospital.appointment.line','appointment_id',string="Lines"
  )
  total_qty = fields.Float(
    compute='_compute_total_qty', string="Total_Quantity", store=True
  )
  date_of_birth = fields.Date(related="patient_id.date_of_birth", groups="om_hospital.group_hospital_doctors")

  # for generating sequences for each record
  @api.model_create_multi
  def create(self, vals_list):
    for vals in vals_list:
      if not vals.get('reference') or vals['reference'] == "New":
        vals['reference'] = self.env["ir.sequence"].next_by_code("hospital.appointment")
    return super().create(vals_list)
  
  # show a concatenation instead of showing primary key for dropdown
  def _compute_display_name(self):
    for rec in self:
      rec.display_name = f"[{rec.reference}] {rec.patient_id.name}"
  
  # add up quantity amount in record matrix row
  @api.depends('appointment_line_ids','appointment_line_ids.qty')
  def _compute_total_qty(self):
    for rec in self:
      rec.total_qty = sum(rec.appointment_line_ids.mapped('qty'))
  
  # add click event to buttons as it tracks state in breadcrumbs
  def action_confirm(self):
    for rec in self:
      # rec.state = "confirmed" #original commented out


      # Different ORM Methods:
      # search, ref, browse, exists, create, write, copy, unlink, default_get, search_count, name_get, name_search, filtered, sudo, with-context      


      # odoo search
      # patients = self.env['hospital.patient'].search([])
      # print("Patients... ",patients)
      # female_patients1 = self.env['hospital.patient'].search([('gender','=','female'),('patient_age','>=',30)]) # query with 'AND'
      # female_patients2 = self.env['hospital.patient'].search(['|', ('gender','=','female'),('patient_age','>=',30)]) # query with 'OR'
      # print("Female Patients 1: ",female_patients1)
      # print("Female Patients 2: ",female_patients2)


      # odoo search count
      # patient_count = self.env['hospital.patient'].search_count([])
      # print("Patient Count:", patient_count)
      # female_patient_count = self.env['hospital.patient'].search_count([('gender','=','female')])
      # print("Female Patient Count:", female_patient_count)


      # odoo ref
      # om_patient = self.env.ref('om_hospital.view_hospital_patient_list')
      # print("OM Patient:", om_patient)


      # odoo browse + exists
      # browse_output = self.env['hospital.patient'].browse(1) # enter record id
      # print("Browse:", browse_output)
      # if browse_output.exists():
      #   print("Output found!")
      # else:
      #   print("Output not found!")


      # odoo create
      # data = {
      #   'name': 'Test',
      #   'gender': 'male'
      # }
      # self.env['hospital.patient'].create(data)

      
      # odoo write (update)
      # record_to_update = self.env['hospital.patient'].browse(1) # enter record id
      # if record_to_update.exists():
      #   data = {
      #     'gender': 'female'
      #   }
      #   record_to_update.write(data)


      # odoo copy (duplicate)
      # record_to_copy = self.env['hospital.patient'].browse(1) # enter record id
      # record_to_copy.copy()


      # odoo unlink (delete)
      # record_to_del = self.env['hospital.patient'].browse(5) # enter record id
      # record_to_del.unlink()

      # odoo.. 



  def action_ongoing(self):
    for rec in self:
      rec.state = "ongoing"

  def action_done(self):
    for rec in self:
      rec.state = "done"
  
  def action_cancel(self):
    for rec in self:
      rec.state = "cancel"


class HospitalAppointmentLine(models.Model):
  _name = 'hospital.appointment.line'
  _description = 'Hospital Appointment Line'

  appointment_id = fields.Many2one('hospital.appointment', string="Appointment")
  product_id = fields.Many2one('product.product', string="Product", required=True)
  qty = fields.Float(string="Quantity")
