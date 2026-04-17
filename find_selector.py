"""
linkareer 직무 검색란 selector 확인 스크립트
실행 후 출력된 정보를 보고 직무 input의 정확한 selector를 파악합니다.
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time, json

def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )
    return driver

driver = get_driver()
driver.get("https://linkareer.com/cover-letter/search?sort=RELEVANCE")
print("페이지 로딩 중... (5초 대기)")
time.sleep(5)

# ── 모든 input 요소 출력 ──────────────────────────────
print("\n" + "="*60)
print("[ 페이지의 모든 input 요소 ]")
print("="*60)
inputs_info = driver.execute_script("""
    var inputs = document.querySelectorAll('input');
    var result = [];
    inputs.forEach(function(inp, i) {
        var rect = inp.getBoundingClientRect();
        var parent = inp.parentElement;
        var grandparent = parent ? parent.parentElement : null;
        result.push({
            index: i,
            type: inp.type,
            placeholder: inp.placeholder,
            name: inp.name,
            id: inp.id,
            className: inp.className.substring(0, 80),
            value: inp.value,
            visible: rect.width > 0 && rect.height > 0,
            parent_text: parent ? parent.innerText.replace(/\\n/g,' ').substring(0,80) : '',
            grandparent_text: grandparent ? grandparent.innerText.replace(/\\n/g,' ').substring(0,80) : ''
        });
    });
    return result;
""")

for info in inputs_info:
    print(f"\n  [{info['index']}] type={info['type']} | visible={info['visible']}")
    print(f"       placeholder = '{info['placeholder']}'")
    print(f"       name        = '{info['name']}'")
    print(f"       id          = '{info['id']}'")
    print(f"       class       = '{info['className']}'")
    print(f"       parent_text = '{info['parent_text']}'")

# ── 직무 관련 텍스트 주변 요소 출력 ──────────────────
print("\n" + "="*60)
print("[ '직무' 텍스트 포함 요소 ]")
print("="*60)
job_elements = driver.execute_script("""
    var all = document.querySelectorAll('*');
    var result = [];
    all.forEach(function(el) {
        if (el.children.length === 0 && el.innerText && el.innerText.includes('직무')) {
            var rect = el.getBoundingClientRect();
            result.push({
                tag: el.tagName,
                text: el.innerText.substring(0,100),
                className: el.className.substring(0,80),
                visible: rect.width > 0
            });
        }
    });
    return result.slice(0, 20);
""")
for el in job_elements:
    print(f"  <{el['tag']}> class='{el['className']}' text='{el['text']}' visible={el['visible']}")

# ── 현재 URL 출력 ──────────────────────────────
print("\n" + "="*60)
print(f"[ 현재 URL ] {driver.current_url}")
print("="*60)

input("\n브라우저를 확인하세요. 종료하려면 Enter 키를 누르세요...")
driver.quit()
