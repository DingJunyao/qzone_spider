from qzone_spider import json_parse
import logging
import json

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(name)s: %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

fl = open('../../example/newest_example/rough.json', 'r', encoding='utf-8')
rough = json.load(fl)
fl.close()
for i in range(len(rough)):
    fl_fine = open('../../example/newest_example/fine_%s.json' % i, 'r', encoding='utf-8')
    fine = json.load(fl_fine)
    fl_fine.close()
    parse = json_parse.rough_json_parse(rough, i)
    print(json.dumps(parse, ensure_ascii=False))
    parse = json_parse.fine_json_parse(rough, i, fine)
    print(json.dumps(parse, ensure_ascii=False))
