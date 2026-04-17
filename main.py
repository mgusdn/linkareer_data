from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time, json, re, urllib.parse

KEYWORD    = "백엔드 개발자"
OUTPUT     = "cover_letters.jsonl"

def get_driver(headless=False):
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )
    driver.set_page_load_timeout(30)
    return driver

def get_search_url(keyword, page=1):
    encoded = urllib.parse.quote_plus(keyword)
    base = f"https://linkareer.com/cover-letter/search?role={encoded}&sort=PASSED_AT&tab=all"
    return base if page == 1 else f"{base}&page={page}"

def get_result_links(driver, keyword, page=1):
    """검색 결과 페이지에서 자소서 링크만 추출"""
    driver.get(get_search_url(keyword, page))
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='coverletter-content']"))
        )
    except:
        return []
    time.sleep(2)

    links = driver.execute_script("""
        var results = [];
        var seen = new Set();
        document.querySelectorAll('[class*="coverletter-content"]').forEach(function(el) {
            var node = el;
            while (node && node.tagName !== 'A') node = node.parentElement;
            if (node && node.href) {
                var href = node.href.split('?')[0];
                if (/\\/cover-letter\\/\\d+/.test(href) && !seen.has(href)) {
                    seen.add(href);
                    results.push(href);
                }
            }
        });
        return results;
    """)
    return links

def get_all_links(driver, keyword):
    """모든 페이지를 순회하며 링크 수집"""
    all_links = []
    page = 1
    while True:
        print(f"  검색 페이지 {page} 수집 중...", end=" ", flush=True)
        links = get_result_links(driver, keyword, page)
        print(f"{len(links)}건")
        if not links:
            break
        all_links.extend(links)
        page += 1
    return all_links

def parse_cover_letter(driver, url, keyword):
    try:
        driver.get(url)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )
        time.sleep(2)
    except:
        print(f"  로딩 실패: {url}")
        return None

    data = {
        "url": url,
        "keyword": keyword,
        "company": "",
        "job": "",
        "season": "",
        "spec": "",
        "questions": []
    }

    try:
        # 기업명 / 직무 / 시즌
        h1 = driver.find_element(By.TAG_NAME, "h1").text.strip()
        parts = [p.strip() for p in h1.split("/")]
        data["company"] = parts[0] if len(parts) > 0 else ""
        data["season"]  = parts[-1] if len(parts) > 1 else ""
        data["job"]     = " / ".join(parts[1:-1]) if len(parts) > 2 else (parts[1] if len(parts) == 2 else "")

        # 합격 스펙
        try:
            data["spec"] = driver.find_element(By.TAG_NAME, "h3").text.strip()
        except:
            pass

        # 문항 + 답변 파싱
        body = driver.find_element(By.TAG_NAME, "body").text

        match = re.search(r'문장 스크랩\n[-]+\n복사\n[-]+\n공유\n(.+?)\n새창', body, re.DOTALL)
        content = match.group(1).strip() if match else body

        numbered = re.split(r'\n(?=\d+\.\s)', content)
        if len(numbered) > 1:
            for section in numbered:
                lines = section.strip().split("\n", 1)
                if len(lines) == 2 and re.match(r'^\d+\.', lines[0]):
                    data["questions"].append({
                        "question": lines[0].strip(),
                        "answer":   lines[1].strip()
                    })
        else:
            data["questions"].append({
                "question": "[자유양식]",
                "answer":   content.strip()
            })

    except Exception as e:
        print(f"  파싱 오류: {e}")

    return data

def main():
    driver = get_driver(headless=False)

    try:
        print(f"\n검색어: {KEYWORD}")
        print("=" * 50)

        print("\n[1단계] 자소서 링크 전체 수집...")
        links = get_all_links(driver, KEYWORD)
        print(f"총 {len(links)}개 링크 수집 완료\n")

        print(f"[2단계] 상세 페이지 수집 → {OUTPUT}")
        success, fail = 0, 0

        with open(OUTPUT, "w", encoding="utf-8") as f:
            for idx, link in enumerate(links, 1):
                print(f"  [{idx:02d}/{len(links)}] {link}", end=" ... ", flush=True)
                result = parse_cover_letter(driver, link, KEYWORD)
                if result:
                    f.write(json.dumps(result, ensure_ascii=False) + "\n")
                    success += 1
                    print("완료")
                else:
                    fail += 1
                    print("실패")
                time.sleep(2.5)

        print(f"\n완료: 성공 {success}건 / 실패 {fail}건 → {OUTPUT}")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
