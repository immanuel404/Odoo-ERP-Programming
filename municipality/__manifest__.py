{
  "name": "Municipality System",
  "author": "Trutech Solutions",
  "summary": "Test Module",
  "version": "18.0.0.0.0",
  "license": "OEEL-1",
  "depends": [
    'mail',
    'account',
    'product'
  ],
  "data": [
    "security/ir.model.access.csv",
    "data/ir_sequence.xml",
    # "data/cron_job.xml",
    "views/erf_views.xml",
    "views/contract_views.xml",
    "views/dynamic_field.xml",
    "views/meter_reading_views.xml",
    'views/mun_meter_report.xml',
    'views/mun_meter_report_action.xml',
    "views/meter_views.xml",
    "views/menu.xml",
  ],
  'installable': True,
  'application': False,
}
