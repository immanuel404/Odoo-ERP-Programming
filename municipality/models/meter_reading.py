from odoo import api,fields,models,_
from odoo.exceptions import ValidationError
from datetime import date,datetime,timedelta


class MeterReading(models.Model):
  _name = "meter.reading"
  _inherit = ['mail.thread']
  _description = "Meter Reading Master"
 
  meter_no = fields.Many2one('mun.meter', string="Meter No.", ondelete="restrict", tracking=True)
  contract = fields.Char(string="Contract", required=True, tracking=True)
  erf = fields.Char(string="ERF", required=True, tracking=True)
  start_date = fields.Date(string="Start Date", required=True, tracking=True)
  end_date = fields.Date(string="End Date", required=True, tracking=True)
  reading_type = fields.Selection([
    ("actual","Actual"),("estimate","Estimate")
  ], default='', required=True, tracking=True)
  prev_reading = fields.Integer(string="Previous Reading", tracking=True)
  curr_reading = fields.Integer(string="Current Reading", tracking=True)
  usage = fields.Integer(string="Usage", tracking=True)


  # on-change contract field
  @api.onchange('meter_no')
  def _onchange_contract(self):
    if self.meter_no:
      self.contract = self.meter_no.contract.reference
      self.erf = self.meter_no.erf

      # find last reading
      last_reading = self.env['meter.reading'].search([('contract','=',self.contract)], order='end_date desc', limit=1)
      
      # Get the current month and year
      current_month = date.today().month
      current_year = date.today().year
      if last_reading and last_reading.start_date:
        # Check if the last reading is in the current month and year
        last_reading_month = last_reading.start_date.month
        last_reading_year = last_reading.start_date.year
        if last_reading_month == current_month and last_reading_year == current_year:
          raise ValidationError("A reading already exists in the current month.")
      
        self.prev_reading = last_reading.curr_reading
      else:
        self.prev_reading = 0


  # automatically populate the end_date with the last day of the same month
  @api.onchange('start_date')
  def _onchange_start_date(self):
    for record in self:
      if record.start_date:
        
        # find last reading
        last_reading = self.env['meter.reading'].search([('contract','=',self.contract)], order='end_date desc', limit=1) 
        if last_reading and last_reading.start_date:
          # Compare the month and year of the last reading and the current start date
          last_reading_month = last_reading.start_date.month
          last_reading_year = last_reading.start_date.year
          current_month = record.start_date.month
          current_year = record.start_date.year
          # Check if the last reading is in the same month or more recent
          if (last_reading_year > current_year or (last_reading_year == current_year and last_reading_month >= current_month)):
            raise ValidationError(
              "Invalid date. / A reading already exists for this period."
            )

        # add end_date to field
        first_day_next_month = (record.start_date.replace(day=1) + timedelta(days=32)).replace(day=1)
        last_day = first_day_next_month - timedelta(days=1)
        record.end_date = last_day


  # automatically populate the usage
  @api.onchange('curr_reading')
  def _onchange_curr_reading(self):
    for record in self:
      if record.curr_reading:
        self.usage = record.curr_reading - record.prev_reading