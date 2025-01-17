from odoo import models


class MyReport(models.AbstractModel):
  _name = 'my.report'
  _description = 'My Report'
  _inherit = ['mail.thread']

  def _get_report_values(self, docids, data=None):
    docs = self.env['mun.meter'].browse(docids)
    return {
      'docs': docs,
    }
