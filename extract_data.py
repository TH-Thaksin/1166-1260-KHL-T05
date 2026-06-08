"""
extract_data.py — Tạo data.js cho web app phân tích chất lượng ĐTV
Đọc: merge 5.csv (CNTT 18001260) + merge 6.csv (BRCĐ 18001166)
Output: data.js (root)
"""
import csv
import json
import os
from collections import defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
MERGE5  = os.path.join(BASE, 'merge 5.csv')
MERGE6  = os.path.join(BASE, 'merge 6.csv')
OUT_DIR = BASE
OUT     = os.path.join(OUT_DIR, 'data.js')

CRITERIA = [
    '1.1.1','1.1.2','1.1.3','1.1.4','1.1.5',
    '1.2.1','1.2.2','1.2.3','1.2.4','1.2.5',
    '1.3.1','1.3.2',
    '2.1','2.2','2.3',
    '3.1','3.2','3.3','3.4',
    '4.1','4.2','4.3','4.4','4.5','4.6'
]

# Expected value to PASS (violation = actual differs from this, excluding N/A)
EXPECTED = {
    '1.1.1':'Có','1.1.2':'Có','1.1.3':'Có','1.1.4':'Có','1.1.5':'Có',
    '1.2.1':'Có','1.2.2':'Có','1.2.3':'Có','1.2.4':'Có','1.2.5':'Có',
    '1.3.1':'Có','1.3.2':'Có',
    '2.1':'Có','2.2':'Có','2.3':'Không',
    '3.1':'Có','3.2':'Có','3.3':'Có','3.4':'Có',
    '4.1':'Có','4.2':'Có','4.3':'Không','4.4':'Có','4.5':'Có','4.6':'Không',
}

CNTT_BASE = 'https://cntt-beige.vercel.app'
ACAD_BASE = 'https://1166-academy-v1-0.vercel.app'
KB   = ACAD_BASE + '/kien-thuc/kbcg-khung-kich-ban'
KN   = ACAD_BASE + '/kien-thuc/ky-nang-mem'
KH   = ACAD_BASE + '/kien-thuc/kbhkh-bao-hong'
ESC  = ACAD_BASE + '/kien-thuc/escalate-sms-3-muc'
HG   = ACAD_BASE + '/kien-thuc/hengio-thanh-thai'
TQ   = ACAD_BASE + '/kien-thuc/tong-quan-1166'
HT   = ACAD_BASE + '/kien-thuc/he-thong-cong-cu'
TL   = ACAD_BASE + '/kien-thuc/thanhly-quy-trinh'
CM   = ACAD_BASE + '/kien-thuc/cam-mesh-tu-van'

CRITERIA_META = {
    '1.1.1': {
        'label': 'Chào hỏi khách hàng',
        'group': 'Nghiệp vụ', 'reminder': True,
        'tip': 'Phải chào ngay khi nhận máy, giới thiệu đúng cú pháp chuẩn.',
        'example': 'Dạ, Chăm sóc khách hàng VNPT xin nghe ạ',
        'learnCNTT': KB, 'learnBRCD': KB,
    },
    '1.1.2': {
        'label': 'Mời khách hàng nêu yêu cầu',
        'group': 'Nghiệp vụ', 'reminder': True,
        'tip': 'Sau chào hỏi phải mời KH nêu yêu cầu một cách chủ động.',
        'example': 'Em có thể hỗ trợ gì cho Anh/Chị ạ?',
        'learnCNTT': KB, 'learnBRCD': KB,
    },
    '1.1.3': {
        'label': 'Xác minh thông tin định danh KH',
        'group': 'Nghiệp vụ', 'reminder': False,
        'tip': 'Xác minh số ĐT, tên, CCCD, mã thuê bao TRƯỚC khi hỗ trợ.',
        'example': 'Anh/Chị cho em xin số điện thoại đăng ký dịch vụ được không ạ?',
        'learnCNTT': KB, 'learnBRCD': TQ,
    },
    '1.1.4': {
        'label': 'Nhận diện khách hàng',
        'group': 'Nghiệp vụ', 'reminder': False,
        'tip': 'Tra cứu thông tin KH từ hệ thống để nhận diện (VIP, lịch sử, loại dịch vụ).',
        'example': 'Em đã kiểm tra thông tin anh/chị, tài khoản đang dùng gói...',
        'learnCNTT': HT, 'learnBRCD': HT,
    },
    '1.1.5': {
        'label': 'Xác định đúng nhu cầu khách hàng',
        'group': 'Nghiệp vụ', 'reminder': False,
        'tip': 'Xác nhận lại nhu cầu trước khi xử lý để tránh hiểu sai.',
        'example': 'Anh/Chị cần em hỗ trợ [vấn đề X] đúng không ạ?',
        'learnCNTT': CM, 'learnBRCD': CM,
    },
    '1.2.1': {
        'label': 'Xác định loại lỗi khách hàng gặp',
        'group': 'Nghiệp vụ', 'reminder': False,
        'tip': 'Phân loại lỗi: kỹ thuật / thao tác / dịch vụ / hệ thống — trước khi xử lý.',
        'example': 'Để em kiểm tra xem lỗi này thuộc về kỹ thuật hay thao tác nhé ạ',
        'learnCNTT': CNTT_BASE, 'learnBRCD': KH,
    },
    '1.2.2': {
        'label': 'Tra cứu thông tin hệ thống nội bộ',
        'group': 'Nghiệp vụ', 'reminder': False,
        'tip': 'Luôn tra cứu hệ thống trước khi trả lời để đảm bảo thông tin chính xác.',
        'example': 'Anh/Chị chờ em kiểm tra thông tin trên hệ thống một chút ạ',
        'learnCNTT': HT, 'learnBRCD': KH,
    },
    '1.2.3': {
        'label': 'Giải quyết ngay hoặc chuyển tuyến sau',
        'group': 'Nghiệp vụ', 'reminder': False,
        'tip': 'Nếu không giải quyết được ngay → chuyển trưởng ca/GQKN. Không để KH chờ vô hạn.',
        'example': 'Em xin chuyển máy sang bộ phận chuyên trách để hỗ trợ anh/chị tốt hơn ạ',
        'learnCNTT': KH, 'learnBRCD': KH,
    },
    '1.2.4': {
        'label': 'Chuyển nội dung cho tuyến sau',
        'group': 'Nghiệp vụ', 'reminder': False,
        'tip': 'Ghi đầy đủ nội dung cần xử lý khi chuyển tuyến sau theo đúng quy trình.',
        'example': 'Em đã ghi nhận yêu cầu và chuyển bộ phận X xử lý cho anh/chị ạ',
        'learnCNTT': ESC, 'learnBRCD': ESC,
    },
    '1.2.5': {
        'label': 'Hẹn thời gian gọi lại cho khách hàng',
        'group': 'Nghiệp vụ', 'reminder': False,
        'tip': 'Luôn xác nhận thời gian dự kiến xử lý CỤ THỂ, không nói chung chung.',
        'example': 'Em hẹn trong vòng 24h làm việc sẽ phản hồi lại anh/chị ạ',
        'learnCNTT': HG, 'learnBRCD': HG,
    },
    '1.3.1': {
        'label': 'Hỏi KH cần hỗ trợ thêm (cuối gọi)',
        'group': 'Nghiệp vụ', 'reminder': True,
        'tip': 'Bước bị bỏ qua nhiều nhất! Luôn hỏi TRƯỚC khi kết thúc cuộc gọi.',
        'example': 'Anh/Chị có cần em hỗ trợ thêm vấn đề gì nữa không ạ?',
        'learnCNTT': KB, 'learnBRCD': KB,
    },
    '1.3.2': {
        'label': 'Cảm ơn và chào tạm biệt',
        'group': 'Nghiệp vụ', 'reminder': True,
        'tip': 'Kết thúc lịch sự bằng lời cảm ơn trước khi gác máy.',
        'example': 'Cảm ơn anh/chị đã liên hệ VNPT. Chúc anh/chị một ngày tốt lành ạ!',
        'learnCNTT': KB, 'learnBRCD': KB,
    },
    '2.1': {
        'label': 'Thái độ tích cực, tôn trọng KH',
        'group': 'Thái độ', 'reminder': False,
        'tip': 'Giữ giọng nói nhẹ nhàng, lịch sự trong suốt cuộc gọi dù KH có bực bội.',
        'example': 'Em rất hiểu sự bất tiện của anh/chị, em sẽ cố gắng giải quyết nhanh nhất',
        'learnCNTT': KN, 'learnBRCD': KN,
    },
    '2.2': {
        'label': 'Chuyên nghiệp với khách hàng khó tính',
        'group': 'Thái độ', 'reminder': False,
        'tip': 'Khi KH gay gắt → giữ bình tĩnh, không phản bác, không thay đổi giọng điệu.',
        'example': 'Em hiểu anh/chị đang rất bức xúc, em xin lỗi về sự bất tiện này',
        'learnCNTT': KN, 'learnBRCD': KN,
    },
    '2.3': {
        'label': 'Khách hàng phàn nàn thái độ ĐTV',
        'group': 'Thái độ', 'reminder': False,
        'tip': 'Vi phạm nghiêm trọng. Không để KH yêu cầu chuyển lãnh đạo vì thái độ.',
        'example': None,
        'learnCNTT': KN, 'learnBRCD': KN,
    },
    '3.1': {
        'label': 'Cam kết trách nhiệm bằng lời',
        'group': 'Tinh thần trách nhiệm', 'reminder': False,
        'tip': 'Dùng từ ngữ cam kết CỤ THỂ, không nói chung chung.',
        'example': 'Em sẽ kiểm tra ngay và gọi lại cho anh/chị trong vòng 30 phút',
        'learnCNTT': KB, 'learnBRCD': KB,
    },
    '3.2': {
        'label': 'Xử lý/chuyển tiếp + cập nhật tình hình',
        'group': 'Tinh thần trách nhiệm', 'reminder': False,
        'tip': 'Khi bộ phận khác đang xử lý → chủ động cập nhật tiến độ cho KH.',
        'example': 'Hiện tại bộ phận kỹ thuật đang xử lý, dự kiến hoàn thành lúc...',
        'learnCNTT': TL, 'learnBRCD': TL,
    },
    '3.3': {
        'label': 'Giải thích rõ khi KH không nghe/hiểu',
        'group': 'Tinh thần trách nhiệm', 'reminder': False,
        'tip': 'Khi KH không hiểu → kiên nhẫn giải thích lại theo cách khác, không lặp y nguyên.',
        'example': 'Để em giải thích lại theo cách khác ạ, anh/chị vui lòng...',
        'learnCNTT': KN, 'learnBRCD': KN,
    },
    '3.4': {
        'label': 'Chủ động giải thích khi KH không hài lòng',
        'group': 'Tinh thần trách nhiệm', 'reminder': False,
        'tip': 'Khi KH bày tỏ không hài lòng → chủ động giải thích nguyên nhân và hướng giải quyết.',
        'example': 'Em hiểu anh/chị chưa hài lòng, để em giải thích rõ hơn về...',
        'learnCNTT': KN, 'learnBRCD': KN,
    },
    '4.1': {
        'label': 'Dùng từ ngữ thể hiện sự cảm thông',
        'group': 'Kỹ năng giao tiếp', 'reminder': False,
        'tip': 'Thường xuyên dùng: "Dạ", "Vâng", "Em hiểu ạ", "Em xin lỗi", "Em rất tiếc".',
        'example': 'Dạ, em hoàn toàn hiểu sự bất tiện của anh/chị ạ',
        'learnCNTT': KN, 'learnBRCD': KB,
    },
    '4.2': {
        'label': 'Ngôn ngữ lịch sự, xưng hô phù hợp',
        'group': 'Kỹ năng giao tiếp', 'reminder': False,
        'tip': 'Xưng "em", gọi KH là "anh/chị". Không dùng từ địa phương không phổ thông.',
        'example': 'Dạ thưa anh/chị, em xin...',
        'learnCNTT': KN, 'learnBRCD': KN,
    },
    '4.3': {
        'label': 'Ngắt lời không nói "xin lỗi/xin phép"',
        'group': 'Kỹ năng giao tiếp', 'reminder': False,
        'tip': 'Khi cần ngắt lời phải nói "Em xin phép" hoặc "Xin lỗi anh/chị" trước.',
        'example': 'Em xin phép được bổ sung thêm thông tin ạ...',
        'learnCNTT': KN, 'learnBRCD': KN,
    },
    '4.4': {
        'label': 'Thông báo khi yêu cầu khách hàng chờ',
        'group': 'Kỹ năng giao tiếp', 'reminder': False,
        'tip': 'Khi cần tra cứu hoặc chuyển máy → thông báo trước và xin phép KH.',
        'example': 'Anh/Chị vui lòng chờ em khoảng 30 giây để tra cứu thông tin ạ',
        'learnCNTT': KB, 'learnBRCD': KN,
    },
    '4.5': {
        'label': 'Diễn đạt ngắn gọn, không dùng từ địa phương',
        'group': 'Kỹ năng giao tiếp', 'reminder': False,
        'tip': 'Nói ngắn gọn, rõ ràng. Tránh từ địa phương khó hiểu hoặc biệt ngữ nội bộ.',
        'example': None,
        'learnCNTT': KN, 'learnBRCD': KB,
    },
    '4.6': {
        'label': 'Lặp lại thông tin không cần thiết',
        'group': 'Kỹ năng giao tiếp', 'reminder': False,
        'tip': 'Chỉ nhắc lại thông tin khi KH yêu cầu hoặc cần xác nhận. Không lặp đi lặp lại.',
        'example': None,
        'learnCNTT': KN, 'learnBRCD': KN,
    },
}


def extract_location(unit, account_id=''):
    text = (unit + account_id).upper()
    if 'HAN' in text: return 'HAN'
    if 'DNG' in text: return 'DNG'
    if 'HCM' in text: return 'HCM'
    return 'KHÁC'


def is_violation(c, val):
    expected = EXPECTED.get(c)
    if not expected or not val: return False
    v = val.strip()
    if v in ('Không áp dụng', ''): return False
    return v != expected


def is_applicable(val):
    if not val: return False
    return val.strip() not in ('Không áp dụng', '')


def process_csv(filepath, include_calls=True, hotline_filter=None):
    agents = {}
    total_calls = 0
    sat_count = 0
    not_sat_count = 0
    na_count = 0
    c_violations = defaultdict(int)
    c_applicable = defaultdict(int)

    with open(filepath, encoding='utf-8-sig', errors='replace') as f:
        reader = csv.DictReader(f)
        for row in reader:
            hotline = row.get('Đầu số tổng đài', '').strip()
            if hotline_filter and hotline != hotline_filter:
                continue

            name = row.get('Họ tên ĐTV', '').strip()
            if not name:
                continue

            acct  = row.get('Tài khoản', '').strip()
            unit  = row.get('Đơn vị', '').strip()
            key   = acct or name

            if key not in agents:
                agents[key] = {
                    'name': name, 'accountId': acct, 'unit': unit,
                    'location': extract_location(unit, acct),
                    'totalCalls': 0,
                    'cv': defaultdict(int),   # criteria violations
                    'ca': defaultdict(int),   # criteria applicable
                    'sn': [], 'st': [], 'sr': [], 'sk': [],  # score lists
                    'calls': [],
                }
            a = agents[key]
            a['totalCalls'] += 1
            total_calls += 1

            sat = row.get('Đánh giá hài lòng', '').strip()
            if sat == 'hài lòng':      sat_count += 1
            elif sat == 'không hài lòng': not_sat_count += 1
            else:                          na_count += 1

            call_viols = []
            for c in CRITERIA:
                val = row.get(c, '').strip()
                if is_applicable(val):
                    c_applicable[c] += 1
                    a['ca'][c] += 1
                    if is_violation(c, val):
                        c_violations[c] += 1
                        a['cv'][c] += 1
                        call_viols.append(c)

            for key2, col, lst in [
                (a, 'Điểm tuân thủ quy trình',   'sn'),
                (a, 'Điểm thái độ chuyên nghiệp', 'st'),
                (a, 'Điểm tinh thần trách nhiệm', 'sr'),
                (a, 'Điểm kỹ năng giao tiếp',     'sk'),
            ]:
                try:
                    v = float(row.get(col, '') or 0)
                    if v > 0: a[lst].append(v)
                except Exception:
                    pass

            if include_calls:
                summary = (row.get('Tóm tắt hội thoại') or '').replace('\n', ' ').strip()[:600]
                a['calls'].append({
                    'id':       row.get('ID cuộc gọi', ''),
                    'time':     row.get('Thời điểm cuộc gọi', ''),
                    'duration': row.get('Thời lượng cuộc gọi', ''),
                    'satisfaction': sat,
                    'url':      row.get('URL', ''),
                    'summary':  summary,
                    'negativeMarkers': (row.get('Dấu hiệu tiêu cực') or '')[:100],
                    'violations': call_viols,
                })

    def avg(lst):
        return round(sum(lst) / len(lst), 2) if lst else 10.0

    result_agents = []
    for a in agents.values():
        cv  = dict(a['cv'])
        ca  = dict(a['ca'])
        top = sorted(cv.items(), key=lambda x: -x[1])
        result_agents.append({
            'name':       a['name'],
            'accountId':  a['accountId'],
            'unit':       a['unit'],
            'location':   a['location'],
            'totalCalls': a['totalCalls'],
            'totalViolations': sum(cv.values()),
            'scoreNV':   avg(a['sn']),
            'scoreTD':   avg(a['st']),
            'scoreTNTN': avg(a['sr']),
            'scoreKNGT': avg(a['sk']),
            'criteriaViolations': cv,
            'criteriaApplicable': ca,
            'topViolations': [c for c, _ in top[:5]],
            'calls': a['calls'] if include_calls else [],
        })

    result_agents.sort(key=lambda x: -x['totalViolations'])

    c_stats = []
    for c in CRITERIA:
        v    = c_violations[c]
        appl = c_applicable[c]
        c_stats.append({'id': c, 'violations': v, 'applicable': appl,
                         'pct': round(v/appl*100, 2) if appl else 0})

    return {
        'totalCalls':   total_calls,
        'satCount':     sat_count,
        'notSatCount':  not_sat_count,
        'naCount':      na_count,
        'satRate':      round(sat_count/total_calls*100, 2) if total_calls else 0,
        'criteriaStats': c_stats,
        'agents':       result_agents,
    }


print('Processing merge 5.csv  →  CNTT 18001260 …')
cntt = process_csv(MERGE5, include_calls=True)
cntt['hotline'] = '18001260'
print(f'  {cntt["totalCalls"]} cuộc gọi, {len(cntt["agents"])} ĐTV')

print('Processing merge 6.csv  →  BRCĐ 18001166 …')
brcd = process_csv(MERGE6, include_calls=False, hotline_filter='18001166')
brcd['hotline'] = '18001166'
print(f'  {brcd["totalCalls"]} cuộc gọi, {len(brcd["agents"])} ĐTV')

criteria_list = []
for c in CRITERIA:
    m = CRITERIA_META.get(c, {})
    criteria_list.append({
        'id':        c,
        'label':     m.get('label', c),
        'group':     m.get('group', 'Nghiệp vụ'),
        'reminder':  m.get('reminder', False),
        'passValue': EXPECTED.get(c, 'Có'),
        'tip':       m.get('tip', ''),
        'example':   m.get('example'),
        'learnCNTT': m.get('learnCNTT', CNTT_BASE),
        'learnBRCD': m.get('learnBRCD', ACAD_BASE),
    })

output = {
    'meta': {
        'period':       '05/2026',
        'generatedAt':  '2026-06-08',
        'description':  'Phân tích chất lượng ĐTV tổng đài GĐKH VNPT',
        'cnttAcademy':  CNTT_BASE,
        'brcdAcademy':  ACAD_BASE,
    },
    'criteria': criteria_list,
    'cntt': cntt,
    'brcd': brcd,
}

with open(OUT, 'w', encoding='utf-8') as f:
    f.write('// Auto-generated by extract_data.py — do not edit manually\n')
    f.write('const DATA = ')
    json.dump(output, f, ensure_ascii=False, indent=None, separators=(',', ':'))
    f.write(';\n')

size_mb = os.path.getsize(OUT) / 1024 / 1024
print(f'\n✓ Xong! Output: {OUT}')
print(f'  Kích thước: {size_mb:.1f} MB')
