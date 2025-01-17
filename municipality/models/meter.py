from odoo import api,fields,models,_


class MunMeter(models.Model):
  _name = "mun.meter"
  _inherit = ['mail.thread']
  _description = "Meter Master"
  _rec_name = "meter_no"

  meter_no = fields.Char(string="Meter No.", required=True, tracking=True)
  contract = fields.Many2one('mun.contract', string="Contract", ondelete="restrict")
  client = fields.Char(string="Client", required=True, tracking=True)
  erf = fields.Char(string="ERF", required=True, tracking=True)

  book_no = fields.Char(string="Book No.", required=True, tracking=True)
  alpha_no = fields.Char(string="Alpha No.", required=True, tracking=True)
  lot_no = fields.Char(string="Lot No.", required=True, tracking=True)

  current_month = fields.Integer(string="Current Month's Usage", tracking=True)
  last_month = fields.Integer(string="Last Month's Usage", tracking=True)
  second_last_month = fields.Integer(string="Previous Month's Usage", tracking=True)

  # enter default record data
  @api.model 
  def default_get(self, fields):
    res = super(MunMeter, self).default_get(fields)
    res['meter_no'] = "M"
    return res

  # on-change contract field
  @api.onchange('contract')
  def _onchange_contract(self):
    if self.contract:
      self.client = self.contract.client.name
      self.erf = self.contract.erf


  # cronjob - automate record generation
  def generate_daily_record(self):
    default_contract = self.env['mun.contract'].search([], limit=1)
    # prepare record data
    data = {
      'meter_no': "M003",
      'contract': default_contract.id if default_contract else False,
      'client': default_contract.client.name if default_contract else "Azure Interior",
      'erf': default_contract.erf if default_contract else "1st street",
      'book_no': "03",
      'alpha_no': "03",
      'lot_no': "03",
      'current_month': 0,
      'last_month': 0,
      'second_last_month': 0,
    }
    # create new record
    new_meter = self.create(data)
    return new_meter
  
  
  # button to print report
  def action_print_report(self):
    return self.env.ref('municipality.mun_meter_report').report_action(self)