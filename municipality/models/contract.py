from odoo import api,fields,models
from odoo.exceptions import ValidationError


class MunContract(models.Model):
  _name = "mun.contract"
  _inherit = ['mail.thread']
  _description = "Contract Master"
  _rec_name = "reference"

  reference = fields.Char(string="Contract ID", default="New", readonly=True, copy=False)
  erf = fields.Char(string="ERF", required=True, tracking=True)
  client = fields.Many2one('res.partner',string='Client',required=True,tracking=True)
  start_date = fields.Date(string="Start Date", required=True, tracking=True, default=fields.Date.today)
  end_date = fields.Date(string="End Date", tracking=True)
  approve = fields.Boolean(string='Approved',default=False)

  status = fields.Selection([
    ("active","Active"),("inactive","Inactive")
  ], default='', required=True, tracking=True)
  
  zoning = fields.Selection([
    ("residential","Residential"),("business","Business"),("state business","State Business"),("industrial","Industrial"),("church","Church")
  ], default='', required=True, tracking=True)

  owner_type = fields.Selection([
    ("owner","Owner"),("occuppier","Occuppier")
  ], default='', required=True, tracking=True)

  account_type = fields.Selection([
    ("staff","Staff"),("consumer","Consumer"),("owner","Owner"),("owner/consumer","Owner/Consumer"),("sundries","Sundries"),("housing","Housing"),("other","Other"),("ministry of agriculture","Ministry of Agriculture"),("ministry of education","Ministry of Education"),("ministry of environmnet","Ministry of Environmnet"),("ministry of fisheries and marine","Ministry of Fisheries and Marine"),("ministry of agriculture","Ministry of Agriculture"),("ministry of education","Ministry of Education"),("ministry of environmnet","Ministry of Environmnet"),("ministry of gender","Ministry of Gender"),("ministry of justice","Ministry of Justice"),("dept of civic affairs","Dept of Civic Affairs"),("zambezi regional council","Zambezi Regional Council"),("office of the president","Office of the President"),("school","School"),("office of social service","Office of Social Service"),("ministry of works","Ministry of Works")
  ], default='', required=True, tracking=True)

  contract_item_lines = fields.One2many('mun.contract.items','contract_id', required=True)

  # validation: contract_item_lines -> required
  @api.constrains('contract_item_lines')
  def _check_contract_item_lines(self):
      for record in self:
        if not record.contract_item_lines:
          raise ValidationError("You must add at least one item in the 'Service Charges' field.")
  
  # for generating sequences for each record
  @api.model_create_multi
  def create(self, vals_list):
    for vals in vals_list:
      if not vals.get('reference') or vals['reference'] == "New":
        vals['reference'] = self.env["ir.sequence"].next_by_code("mun.contract")
    return super().create(vals_list)



class MunContractItems(models.Model):
  _name = 'mun.contract.items'
  _description = 'Contract Service Items'
  
  contract_id = fields.Many2one('mun.contract', string="Contract ID")
  product_id = fields.Many2one('product.product', string="Charges", required=True)

