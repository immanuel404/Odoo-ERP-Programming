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

      # find last meter reading
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
        
        # find last meter reading
        reading = self.env['meter.reading'].search([('contract','=',self.contract)], order='end_date desc', limit=1) 
        if reading and reading.start_date:
          reading_month = reading.start_date.month
          reading_year = reading.start_date.year
          current_start_month = record.start_date.month
          current_start_year = record.start_date.year

          # check if the last reading is in the same month or more recent
          if (reading_year == current_start_year and reading_month == current_start_month):
            raise ValidationError("Invalid date! Reading already exists for this period.")
          
          # check if a more recent recent reading exist past the entered date period
          if (reading_year >= current_start_year and reading_month > current_start_month):
            raise ValidationError("Invalid date! A more recent recent reading exists past the entered date period.")
         
          # check is not in future date
          current_date = datetime.today()
          if (current_start_year >= current_date.year and current_start_month > current_date.month):
            raise ValidationError("Invalid date. Start date cannot be in a future month.")

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


  # update readings on save event
  @api.model_create_multi
  def create(self, vals_list):
    for vals in vals_list:

      record = super(MeterReading, self).create(vals)

      meter = self.env['mun.meter'].search([('id', '=', vals.get('meter_no'))], limit=1)
      if not meter:
        raise ValidationError("The selected meter does not exist.")
      
      # if record_to_update:
      current_date = datetime.today()
      data = {}

      # Check if start_date is in the current month
      if record.start_date and record.start_date.month == current_date.month and record.start_date.year == current_date.year:
        data['current_month'] = record.usage

      # Check if start_date is in the previous month
      previous_month_date = current_date.replace(day=1) - timedelta(days=1)
      if record.start_date and record.start_date.month == previous_month_date.month and record.start_date.year == previous_month_date.year:
        data['last_month'] = record.usage

      # Check if start_date is two months back
      two_months_back_date = previous_month_date.replace(day=1) - timedelta(days=1)
      if record.start_date and record.start_date.month == two_months_back_date.month and record.start_date.year == two_months_back_date.year:
        data['second_last_month'] = record.usage

      # Update the related record if data is not empty
      if data:
        meter.write(data)

      return record
    