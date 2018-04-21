from qzone_spider import db_control_postgresql
import json
import logging

logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] %(name)s: %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

for i in range(120):
    fl = open('../../example/parse_example/rough_%s.json' % i, 'r', encoding='utf-8')
    rough = json.load(fl)
    fl.close()
    # fl_fine = open('../../example/parse_example/fine_%s.json' % i, 'r', encoding='utf-8')
    # fine = json.load(fl_fine)
    # fl_fine.close()
    db_control_postgresql.db_write_rough(rough)
