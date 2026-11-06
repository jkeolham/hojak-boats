#!/usr/bin/env python3
"""내 선사 바로가기(hojak-boats) 웹앱 자동 갱신 스크립트.

N100의 reservation-monitor state 파일(/home/ttolmany/scripts/reservation-monitor/state/<날짜>.json)을
읽어 이번 주말(금/토/일)의 탑티어 선사 여유자리와 확인일시를 index.html에 자동 반영한다.
"""
import json
import re
from datetime import date, datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
INDEX_HTML = BASE_DIR / "index.html"
STATE_DIR = Path("/home/ttolmany/scripts/reservation-monitor/state")

# 탑티어 선사 기본 레지스트리 (항구별)
BASE_BOATS = [
    {
        "port": "궁평항",
        "list": [
            {"name": "타이탄호", "url": "http://kungpyeong.com"},
            {"name": "블랙호", "url": "http://kungpyeong.com"},
            {"name": "바다피싱호", "url": "http://gpseafishing.kr"},
        ]
    },
    {
        "port": "전곡항",
        "list": [
            {"name": "제비호", "url": "http://jebi.sunsang24.com"},
            {"name": "스타피싱호", "url": "http://rainbowho.com"},
            {"name": "왕선장호", "url": "http://king.sunsang24.com"},
        ]
    },
    {
        "port": "영흥도",
        "list": [
            {"name": "금강7호", "url": "http://kumkangho.co.kr"},
            {"name": "카리스마호", "url": "http://charisma.sunsang24.com"},
            {"name": "나이스호", "url": "http://niceho.com"},
            {"name": "명성호", "url": "http://xn--hq1b31ko5fzpfdsxrtb.com"},
            {"name": "레전드호", "url": "http://xn--hy1b43d01tuzn.com"},
            {"name": "영진호", "url": "http://youngjinho.net"},
            {"name": "루어피싱호", "url": "http://yhdfish.net"},
            {"name": "팀누리호", "url": "http://xn--od1b68lz1wi4c.kr"},
            {"name": "팀만수호", "url": "https://teammansu.kr"},
        ]
    }
]


def get_weekend_dates(ref_date=None):
    if ref_date is None:
        ref_date = date.today()
    # 월=0, 화=1, 수=2, 목=3, 금=4, 토=5, 일=6
    weekday = ref_date.weekday()
    friday = ref_date + timedelta(days=(4 - weekday))
    saturday = friday + timedelta(days=1)
    sunday = friday + timedelta(days=2)
    return [
        {"key": "fri", "label": "금", "date_obj": friday},
        {"key": "sat", "label": "토", "date_obj": saturday},
        {"key": "sun", "label": "일", "date_obj": sunday},
    ]


def match_boat_data(boat_name, state_boats):
    for key, val in state_boats.items():
        # "타이탄호(궁평항)" 또는 "타이탄호" 매칭
        clean_key = re.sub(r"\(.*?\)", "", key).strip()
        if clean_key == boat_name or key.startswith(boat_name) or boat_name in key:
            return val
    return None


def build(ref_date=None):
    weekend_info = get_weekend_dates(ref_date)
    weekend_array = []
    state_cache = {}

    for w in weekend_info:
        iso = w["date_obj"].isoformat()
        state_file = STATE_DIR / f"{iso}.json"
        checked_str = None
        if state_file.exists():
            try:
                data = json.loads(state_file.read_text(encoding="utf-8"))
                state_cache[w["key"]] = data
                raw_checked = data.get("checked_at")
                if raw_checked:
                    checked_str = raw_checked[:10]
            except Exception as e:
                print(f"[build_boats] state 읽기 오류 ({state_file}): {e}")
        weekend_array.append({
            "key": w["key"],
            "label": w["label"],
            "date": f"{w['date_obj'].month}/{w['date_obj'].day}",
            "iso": iso,
            "checked": checked_str
        })

    # boats 데이터 빌드
    boats_data = []
    for g in BASE_BOATS:
        port_group = {"port": g["port"], "list": []}
        for b in g["list"]:
            boat_item = {
                "name": b["name"],
                "url": b["url"],
                "days": {}
            }
            for w in weekend_info:
                k = w["key"]
                sc = state_cache.get(k)
                if sc and "boats" in sc:
                    matched = match_boat_data(b["name"], sc["boats"])
                    if matched:
                        status = matched.get("status", "미분류")
                        seats = matched.get("seats")
                        url = matched.get("url") or b["url"]
                        boat_item["days"][k] = {
                            "status": status,
                            "seats": seats,
                            "url": url
                        }
                    else:
                        boat_item["days"][k] = None
                else:
                    boat_item["days"][k] = None
            port_group["list"].append(boat_item)
        boats_data.append(port_group)

    # index.html 수정
    content = INDEX_HTML.read_text(encoding="utf-8")

    # var WEEKEND = [...]; 치환
    weekend_json = json.dumps(weekend_array, ensure_ascii=False, indent=4)
    content = re.sub(
        r"var WEEKEND\s*=\s*\[[\s\S]*?\];",
        f"var WEEKEND = {weekend_json};",
        content,
        count=1
    )

    # var boats = [...]; 치환
    boats_json = json.dumps(boats_data, ensure_ascii=False, indent=4)
    content = re.sub(
        r"var boats\s*=\s*\[[\s\S]*?\];",
        f"var boats = {boats_json};",
        content,
        count=1
    )

    # 푸터 갱신 일시
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    content = re.sub(
        r"HOJAK FLEET DISPATCH · [^<]+",
        f"HOJAK FLEET DISPATCH · 최신 자동 갱신 {now_str} (N100 reservation-monitor)",
        content
    )

    INDEX_HTML.write_text(content, encoding="utf-8")
    print(f"[build_boats] 갱신 완료: {INDEX_HTML}")
    print(f"  - 대상 주말: {[w['date'] for w in weekend_array]}")
    for w in weekend_array:
        print(f"  - {w['date']} ({w['label']}): 확인일시={w['checked']}")


def fetch_weekend_states(ref_date=None):
    """이번 주 금/토/일의 탑티어 선사 예약 현황을 최신 크롤링하여 state 디렉터리에 저장한다."""
    import sys
    scripts_dir = "/home/ttolmany/scripts/reservation-monitor"
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    from check_reservations import run_check

    weekend_info = get_weekend_dates(ref_date)
    dates_str = [w["date_obj"].strftime("%m/%d") for w in weekend_info]
    print(f"[build_boats] 이번 주말({dates_str}) 탑티어 선사 크롤링 수집 시작")
    for w in weekend_info:
        iso = w["date_obj"].isoformat()
        print(f"  -> {iso} ({w['label']}요일) 탑티어 선사 실시간 조회 중...")
        try:
            run_check(iso, notify=False, scope="top")
        except Exception as e:
            print(f"  [오류] {iso} 수집 실패: {e}")


def deploy():
    """index.html의 변경 사항을 GitHub Pages (origin/master)에 자동 커밋 및 푸시한다."""
    import os
    import subprocess

    env = os.environ.copy()
    env["PATH"] = f"/home/ttolmany/.local/bin:{env.get('PATH', '')}"

    res = subprocess.run(
        ["git", "status", "--porcelain", "index.html"],
        cwd=str(BASE_DIR),
        capture_output=True,
        text=True,
        check=True
    )
    if not res.stdout.strip():
        print("[build_boats] index.html 내용 변경 없음. GitHub 푸시 생략.")
        return False

    print("[build_boats] index.html 내용 변경 감지 -> 커밋 및 푸시 진행")
    subprocess.run(["git", "add", "index.html"], cwd=str(BASE_DIR), check=True)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    commit_msg = f"chore(auto): update weekend boat reservation status ({now_str})"
    subprocess.run(["git", "commit", "-m", commit_msg], cwd=str(BASE_DIR), check=True, env=env)
    push_res = subprocess.run(
        ["git", "push", "origin", "master"],
        cwd=str(BASE_DIR),
        capture_output=True,
        text=True,
        env=env
    )
    if push_res.returncode == 0:
        print("[build_boats] GitHub 배포(git push) 성공!")
        return True
    else:
        print(f"[build_boats] GitHub 배포 실패: {push_res.stderr}")
        return False


if __name__ == "__main__":
    import sys
    if "--sync" in sys.argv:
        print(f"=== [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] hojak-boats 자동 동기화 및 배포 시작 ===")
        fetch_weekend_states()
        build()
        deploy()
        print(f"=== [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] hojak-boats 자동 동기화 및 배포 완료 ===")
    else:
        build()

