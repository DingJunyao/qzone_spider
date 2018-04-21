from qzone_spider import get_login_info
from qzone_spider import get_json
from qzone_spider import json_parse
import logging
import json
import time

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(name)s: %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

cookie, gtk, qzonetoken = get_login_info.account_login('***REMOVED***', '***REMOVED***')
a = 0
while a <= 100:
    r_cattch_time, a, b = get_json.get_rough_json('***REMOVED***', a, 20, 100, cookie, gtk, qzonetoken)
    a += 1
    for i in range(len(b)):
        f_catch_time, fine = get_json.get_fine_json('***REMOVED***', b[i]['tid'], cookie, gtk, qzonetoken)
        time.sleep(5)
        parse_r = json_parse.rough_json_parse(b, i, r_cattch_time)
        parse_f = json_parse.fine_json_parse(b, i, fine, f_catch_time)
        fl = open('../../example/parse_example/rough_%s.json' % (i + a - 20), 'w', encoding='utf-8')
        fl.write(json.dumps(parse_r, ensure_ascii=False, indent=2))
        fl.close()
        fl = open('../../example/parse_example/fine_%s.json' % (i + a - 20), 'w', encoding='utf-8')
        fl.write(json.dumps(parse_f, ensure_ascii=False, indent=2))
        fl.close()