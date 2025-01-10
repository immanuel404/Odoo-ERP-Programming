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

  current_month = fields.Integer(string="Current Month", tracking=True)
  last_month = fields.Integer(string="Last Month", tracking=True)
  second_last_month = fields.Integer(string="2nd Last Month", tracking=True)

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