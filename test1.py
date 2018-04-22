from qzone_spider import db_control_mysql as db_control
import json
import logging

logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] %(name)s: %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

for i in range(19):
    fl = open('D:\\Code\\qzone_analyse\\example\\newest_example1\\parse\\fine_%s.json' % i, 'r', encoding='utf-8')
    fine = json.load(fl)
    fl.close()
    # fl_fine = open('../../example/parse_example/fine_%s.json' % i, 'r', encoding='utf-8')
    # fine = json.load(fl_fine)
    # fl_fine.close()
    db_control.db_write_fine(fine)
