from qzone_spider import json_parse
import logging
import json

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(name)s: %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

fl = open('D:\\Code\\qzone_analyse\\example\\test_example\\rough.json', 'r', encoding='utf-8')
rough = json.load(fl)
fl.close()
for i in range(len(rough)):
    '''
    fl_fine = open('../../example/newest_example/fine_%s.json' % i, 'r', encoding='utf-8')
    fine = json.load(fl_fine)
    fl_fine.close()
    '''
    parse = json_parse.rough_json_parse(rough, i)
    fl = open('D:\\Code\\qzone_analyse\\example\\test_example\\parse\\rough_%s.json' % i, 'w', encoding='utf-8')
    fl.write(json.dumps(parse, ensure_ascii=False, indent=2))
    fl.close()
    '''
    parse = json_parse.fine_json_parse(rough, i, fine)
    print(json.dumps(parse, ensure_ascii=False))
'''