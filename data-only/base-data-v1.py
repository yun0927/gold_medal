import pandas as pd
import re
import csv  # quoting 옵션 사용을 위해 필요

# 1. CSV 파일 불러오기
df = pd.read_csv('base-data.csv')

# 2. 시간 문자열을 초(float)로 변환하는 함수
def time_to_seconds(t):
    if pd.isna(t) or not isinstance(t, str):
        return None

    t = t.strip().replace('′', "'").replace("’", "'")

    # "1:23.45" 또는 "1:23'45"
    match = re.match(r"(?:(\d+):)?(\d+)[\'\.](\d+)", t)
    if match:
        min_part = int(match.group(1)) if match.group(1) else 0
        sec_part = int(match.group(2))
        frac_part = int(match.group(3))
        frac_seconds = frac_part / (10 ** len(str(frac_part)))
        return min_part * 60 + sec_part + frac_seconds

    # "1:05"
    match_simple = re.match(r"(?:(\d+):)?(\d+)$", t)
    if match_simple:
        min_part = int(match_simple.group(1)) if match_simple.group(1) else 0
        sec_part = int(match_simple.group(2))
        return min_part * 60 + sec_part

    # "45.67" 또는 "59'45"
    match_alt = re.match(r"(\d+)[\'\.](\d+)", t)
    if match_alt:
        sec_part = int(match_alt.group(1))
        frac_part = int(match_alt.group(2))
        frac_seconds = frac_part / (10 ** len(str(frac_part)))
        return sec_part + frac_seconds

    try:
        return float(t)
    except:
        return None

# 3. time → time_sec 변환
df['time_sec'] = df['time'].apply(time_to_seconds)

# 4. 그룹별 순위 계산 (성별, 연령대, 이벤트별) + 정수형으로 변환
df['rank'] = (
    df.groupby(['gender', 'age', 'event'])['time_sec']
    .rank(method='min', ascending=True)
    .astype('Int64')  # Null 허용 정수형
)

# 5. CSV로 저장 (엑셀 열 밀림 방지용 인코딩 + 따옴표 처리)
df.to_csv('ranked_results.csv', index=False, encoding='utf-8-sig', quoting=csv.QUOTE_ALL)

print("✅ 완료: ranked_results.csv 파일이 UTF-8-SIG 형식으로 저장되었습니다.")

