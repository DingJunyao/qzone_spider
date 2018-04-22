from qzone_spider import get_login_info
from qzone_spider import get_json
import logging
import json
import time

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(name)s: %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

cookie, gtk, qzonetoken = get_login_info.account_login('***REMOVED***', '***REMOVED***')

r_catch_time, end, b = get_json.get_rough_json('***REMOVED***', 0, 1, 100, cookie, gtk, qzonetoken)
fl = open('D:\\Code\\qzone_analyse\\example\\test_example\\rough.json', 'w', encoding='utf-8')
fl.write(json.dumps(b, ensure_ascii=False, indent=2))
fl.close()

for i in range(len(b)):
    rough = b[i]
    f_catch_time, fine = get_json.get_fine_json('***REMOVED***', b[i]['tid'], cookie, gtk, qzonetoken)
    fl = open('D:\\Code\\qzone_analyse\\example\\test_example\\fine_' + str(i) + '.json', 'w', encoding='utf-8')
    fl.write(json.dumps(fine, ensure_ascii=False, indent=2))
    fl.close()
    time.sleep(10)
