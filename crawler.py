import time
import random
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import re


class DanawaCrawler:
    def __init__(self):
        """다나와 크롤러 초기화"""
        self.driver = None
        self.setup_driver()
        self.base_url = "https://search.danawa.com/dsearch.php?query="
        
    def setup_driver(self):
        """Chrome 드라이버 설정 (stealth 모드 적용)"""
        chrome_options = Options()
        
        # User-Agent 설정 (최신 Chrome User-Agent)
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36')
        
        # Stealth 모드 설정 (강화)
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # 봇 감지 우회를 위한 추가 설정
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--disable-infobars')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--lang=ko-KR')
        
        # WebDriver 속성 제거를 위한 prefs
        prefs = {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "profile.default_content_setting_values.notifications": 2
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        # 헤드리스 모드 제거 (쿠팡에서 봇 감지 시 필요할 수 있음)
        # chrome_options.add_argument('--headless')
        
        # Selenium 3.x 버전: executable_path 직접 사용
        # 시스템에 설치된 ChromeDriver 확인
        import shutil
        system_chromedriver = shutil.which('chromedriver')
        
        if system_chromedriver:
            # 시스템에 설치된 ChromeDriver 사용
            print(f"시스템 ChromeDriver 사용: {system_chromedriver}")
            executable_path = system_chromedriver
        else:
            # 시스템에 없으면 webdriver-manager로 다운로드 시도
            try:
                print("ChromeDriver 자동 다운로드 시도 중...")
                executable_path = ChromeDriverManager().install()
            except Exception as e:
                print(f"ChromeDriver 자동 다운로드 실패: {e}")
                print("ChromeDriver를 수동으로 설치해주세요:")
                print("  brew install chromedriver")
                raise
        
        try:
            self.driver = webdriver.Chrome(executable_path=executable_path, options=chrome_options)
        except Exception as e:
            if "This version of ChromeDriver only supports Chrome version" in str(e):
                print("\n" + "="*60)
                print("Chrome 브라우저와 ChromeDriver 버전이 일치하지 않습니다.")
                print("="*60)
                print("\n해결 방법:")
                print("1. Chrome 브라우저를 최신 버전으로 업데이트하세요:")
                print("   - Chrome 메뉴 > Chrome 정보 > 자동 업데이트 확인")
                print("2. 또는 다음 명령으로 ChromeDriver를 재설치하세요:")
                print("   brew uninstall chromedriver")
                print("   brew install chromedriver")
                print("\n오류 내용:", str(e))
                print("="*60)
            raise
        
        # JavaScript를 통한 webdriver 속성 제거 및 stealth 모드 강화 (Selenium 3.x 호환)
        # 첫 페이지를 열 때 스크립트 실행
        stealth_script = """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // Chrome 객체 추가
            window.chrome = {
                runtime: {}
            };
            
            // Permissions API 모킹
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
            
            // Plugin 배열 모킹
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            
            // Languages 설정
            Object.defineProperty(navigator, 'languages', {
                get: () => ['ko-KR', 'ko', 'en-US', 'en']
            });
        """
        self.driver.execute_script(stealth_script)
        
    def wait_random(self):
        """5~10초 사이 랜덤 대기 (봇 감지 우회)"""
        wait_time = random.uniform(5, 10)
        time.sleep(wait_time)
        
    def search_products(self, keyword, max_items=70):
        """키워드로 상품 검색 및 데이터 수집"""
        print(f"\n[{keyword}] 검색 시작...")
        
        # URL 인코딩 (한글 키워드 처리)
        import urllib.parse
        encoded_keyword = urllib.parse.quote(keyword)
        url = f"{self.base_url}{encoded_keyword}"
        
        print(f"URL: {url}")
        
        # 다나와 메인 페이지로 먼저 방문 (봇 감지 우회)
        try:
            print("  다나와 메인 페이지 방문 중...")
            self.driver.get("https://www.danawa.com")
            time.sleep(random.uniform(3, 5))
            
            # 페이지가 로드될 때까지 대기
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            except:
                pass
            
            # 메인 페이지에서 자연스러운 행동 시뮬레이션
            time.sleep(random.uniform(2, 4))
            
            # 스크롤 (자연스러운 행동)
            try:
                self.driver.execute_script("window.scrollTo(0, 300);")
                time.sleep(random.uniform(1, 2))
            except:
                pass
            
            print("  다나와 메인 페이지 방문 완료")
        except Exception as e:
            print(f"  메인 페이지 방문 오류: {e}")
        
        # 검색 페이지로 이동하기 전 추가 대기
        time.sleep(random.uniform(2, 4))
        
        # 검색 페이지로 이동
        print("  검색 페이지로 이동 중...")
        self.driver.get(url)
        
        # 페이지 로드 후 대기
        time.sleep(random.uniform(3, 5))
        self.wait_random()
        
        # stealth 스크립트 다시 실행
        try:
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)
        except:
            pass
        
        # 브라우저 창이 살아있는지 확인
        try:
            current_url = self.driver.current_url
            print(f"  현재 페이지: {current_url[:80]}...")
        except Exception as e:
            print(f"  브라우저 오류: {e}")
            return []
        
        products_data = []
        page = 1
        
        # 페이지 로딩 대기 (다나와 페이지 구조)
        try:
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".main_prodlist, .product_list, .prod_list, body"))
            )
        except TimeoutException:
            print("  경고: 페이지 요소를 찾을 수 없습니다. 계속 진행합니다...")
        
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        while len(products_data) < max_items:
            print(f"  페이지 {page} 처리 중... (현재 수집: {len(products_data)}개)")
            
            try:
                # 페이지 로딩 대기 (다나와 상품 리스트 선택자)
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".main_prodlist > li, .product_list > .product_item, .prod_list li"))
                    )
                except TimeoutException:
                    # 다른 선택자 시도
                    try:
                        WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "li.prod_item, .product_item, .item"))
                        )
                    except TimeoutException:
                        print("  경고: 상품 목록을 찾을 수 없습니다.")
                        break
                
                # 스크롤하여 더 많은 상품 로딩 (점진적 스크롤)
                try:
                    # 천천히 스크롤 (자연스러운 행동)
                    scroll_height = self.driver.execute_script("return document.body.scrollHeight")
                    current_position = 0
                    scroll_step = random.randint(300, 600)
                    
                    while current_position < scroll_height:
                        current_position += scroll_step
                        self.driver.execute_script(f"window.scrollTo(0, {current_position});")
                        time.sleep(random.uniform(0.5, 1.5))
                    
                    # 마지막까지 스크롤
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                except:
                    # 스크롤 실패 시 기본 방식
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                
                self.wait_random()
                
                # 상품 리스트 가져오기 (다나와 선택자)
                product_items = self.driver.find_elements(By.CSS_SELECTOR, ".main_prodlist > li, .product_list > .product_item, .prod_list li")
                if not product_items:
                    product_items = self.driver.find_elements(By.CSS_SELECTOR, "li.prod_item, .product_item, .item")
                
                for idx, item in enumerate(product_items):
                    if len(products_data) >= max_items:
                        break
                        
                    try:
                        # 검색 결과 페이지에서 직접 스펙 추출 (상세 페이지 방문 불필요)
                        visit_detail = False
                        product_data = self.extract_product_info(item, visit_detail=visit_detail)
                        if product_data and product_data not in products_data:
                            products_data.append(product_data)
                            print(f"    [{len(products_data)}] {product_data['상품명'][:30]}...")
                            
                    except Exception as e:
                        print(f"    상품 정보 추출 실패: {e}")
                        continue
                
                # 다음 페이지로 이동
                if len(products_data) < max_items:
                    try:
                        # 브라우저 창이 살아있는지 확인
                        try:
                            self.driver.current_url
                        except:
                            print("  브라우저 창이 닫혔습니다.")
                            break
                        
                        # 현재 페이지에서 수집한 상품 수 확인
                        current_page_items = len(product_items)
                        print(f"  현재 페이지에서 {current_page_items}개 상품 발견")
                        
                        # 다음 페이지 버튼 찾기 (다나와)
                        next_button = None
                        next_selectors = [
                            "a[title='다음 페이지']",
                            "a[title*='다음']",
                            ".paging a.next",
                            ".paging .next",
                            "a.paging_next",
                            ".paging_num a:last-child"
                        ]
                        
                        for selector in next_selectors:
                            try:
                                buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                                for btn in buttons:
                                    btn_text = btn.text.strip()
                                    btn_href = btn.get_attribute('href')
                                    # "다음" 텍스트가 있고 href가 있는 버튼 찾기
                                    if ('다음' in btn_text or 'next' in btn_text.lower()) and btn_href:
                                        next_button = btn
                                        break
                                if next_button:
                                    break
                            except:
                                continue
                        
                        if next_button:
                            try:
                                # 다음 페이지로 이동
                                print(f"  다음 페이지로 이동 중... (페이지 {page + 1})")
                                next_button.click()
                                self.wait_random()
                                
                                # 페이지 로드 대기
                                time.sleep(random.uniform(2, 4))
                                
                                # 새로운 페이지 높이 확인
                                last_height = self.driver.execute_script("return document.body.scrollHeight")
                                page += 1
                                
                                # 페이지가 실제로 변경되었는지 확인
                                new_url = self.driver.current_url
                                print(f"  페이지 {page} 로드 완료")
                                
                            except Exception as e:
                                print(f"  다음 페이지 이동 실패: {e}")
                                # 더 이상 수집할 수 없으면 종료
                                if len(products_data) > 0:
                                    print(f"  부분적으로 {len(products_data)}개 수집 완료")
                                break
                        else:
                            print(f"  다음 페이지 버튼을 찾을 수 없습니다. 수집 종료.")
                            if len(products_data) > 0:
                                print(f"  총 {len(products_data)}개 수집 완료")
                            break
                            
                    except Exception as e:
                        print(f"  페이지 이동 오류: {e}")
                        if len(products_data) > 0:
                            print(f"  부분적으로 {len(products_data)}개 수집 완료")
                        break
                        
            except TimeoutException:
                print(f"  페이지 로딩 타임아웃")
                if len(products_data) > 0:
                    print(f"  부분적으로 {len(products_data)}개 수집 완료")
                break
            except Exception as e:
                # 브라우저 창이 닫혔는지 확인
                try:
                    self.driver.current_url
                except:
                    print(f"  브라우저 창이 닫혔습니다. 크롤링 중단.")
                    break
                print(f"  페이지 처리 오류: {e}")
                if len(products_data) > 0:
                    print(f"  부분적으로 {len(products_data)}개 수집 완료")
                break
        
        print(f"[{keyword}] 검색 완료: {len(products_data)}개 수집")
        return products_data
    
    def extract_product_info(self, item, visit_detail=False):
        """개별 상품 정보 추출 (다나와 구조)"""
        try:
            # 상품명 (다나와 선택자)
            product_name = ""
            try:
                name_elem = item.find_element(By.CSS_SELECTOR, ".prod_name, .link_prod, .name, a.prod_name")
                product_name = name_elem.text.strip()
            except:
                try:
                    name_elem = item.find_element(By.CSS_SELECTOR, "a")
                    product_name = name_elem.text.strip()
                except:
                    pass
            
            if not product_name:
                return None
            
            # 상품 URL (다나와)
            product_url = ""
            try:
                link_elem = item.find_element(By.CSS_SELECTOR, "a.prod_name, .link_prod, a")
                product_url = link_elem.get_attribute("href")
                if product_url and not product_url.startswith("http"):
                    product_url = "https://www.danawa.com" + product_url
            except:
                pass
            
            # 가격 (다나와 - 여러 가격 중 최저가)
            price = ""
            try:
                # 다나와는 여러 쇼핑몰 가격을 보여주므로 최저가 추출
                price_elem = item.find_element(By.CSS_SELECTOR, ".price_sect, .low_price, .price, .prod_price")
                price_text = price_elem.text.strip()
                # 숫자만 추출
                price = re.sub(r'[^\d]', '', price_text)
            except:
                # 여러 가격이 있는 경우
                try:
                    price_elems = item.find_elements(By.CSS_SELECTOR, ".price, .low_price")
                    if price_elems:
                        prices = []
                        for p in price_elems:
                            price_text = p.text.strip()
                            price_num = re.sub(r'[^\d]', '', price_text)
                            if price_num:
                                prices.append(int(price_num))
                        if prices:
                            price = str(min(prices))  # 최저가
                except:
                    pass
            
            # 별점 (다나와 검색 결과에서 찾기)
            rating = ""
            try:
                # 여러 선택자 시도
                rating_selectors = [
                    ".rating, .star, .score",
                    ".review_rating, .prod_rating",
                    "[class*='rating']",
                    "[class*='star']",
                    ".grade, .point"
                ]
                for selector in rating_selectors:
                    try:
                        rating_elem = item.find_element(By.CSS_SELECTOR, selector)
                        rating_text = rating_elem.text.strip()
                        rating_match = re.search(r'[\d.]+', rating_text)
                        if rating_match:
                            rating = rating_match.group()
                            break
                    except:
                        continue
            except:
                pass
            
            # 리뷰 수 (다나와 검색 결과에서 찾기)
            review_count = ""
            try:
                # 여러 선택자 시도
                review_selectors = [
                    ".review, .review_count, .comment_count",
                    "[class*='review']",
                    "[class*='comment']",
                    ".review_num, .prod_review"
                ]
                for selector in review_selectors:
                    try:
                        review_elem = item.find_element(By.CSS_SELECTOR, selector)
                        review_text = review_elem.text.strip()
                        review_count = re.sub(r'[^\d]', '', review_text)
                        if review_count:
                            break
                    except:
                        continue
            except:
                pass
            
            # 스펙 정보 추출 (검색 결과 페이지에서 직접 추출)
            specs = ""
            try:
                # 다나와 검색 결과 페이지의 스펙 정보 찾기
                # 실제 구조: .spec-box 또는 .spec-box.spec-box--full
                spec_selectors = [
                    ".spec-box.spec-box--full",  # 전체 스펙이 보이는 경우
                    ".spec-box",  # 기본 스펙 박스
                    ".spec_list"  # 스펙 리스트
                ]
                
                for selector in spec_selectors:
                    try:
                        spec_elem = item.find_element(By.CSS_SELECTOR, selector)
                        spec_text = spec_elem.text.strip()
                        # 의미있는 스펙 정보인지 확인
                        if (spec_text and len(spec_text) > 10 and 
                            '원' not in spec_text and
                            '배송' not in spec_text and
                            '할인' not in spec_text and
                            '쿠팡' not in spec_text and
                            '닫기' not in spec_text and
                            ('/' in spec_text or '인치' in spec_text or 'kg' in spec_text or 'GB' in spec_text or 
                             'cm' in spec_text or 'Hz' in spec_text or '해상도' in spec_text or '밝기' in spec_text or
                             'CPU' in spec_text or '램' in spec_text or '그래픽' in spec_text)):
                            specs = spec_text
                            break
                    except:
                        continue
                
                # 스펙을 찾지 못한 경우 더 넓은 범위로 검색
                if not specs:
                    try:
                        # 전체 아이템의 텍스트에서 스펙 정보 추출
                        item_text = item.text
                        # 스펙 패턴 찾기 (예: "노트북 / 39.6cm(15.6인치) / 1.75kg" 같은 형식)
                        lines = item_text.split('\n')
                        spec_parts = []
                        for line in lines:
                            line = line.strip()
                            # 스펙으로 보이는 라인 찾기
                            if (line and len(line) > 5 and
                                '원' not in line and
                                '배송' not in line and
                                '할인' not in line and
                                '쿠팡' not in line and
                                ('/' in line or '인치' in line or 'kg' in line or 'GB' in line or 'cm' in line or 
                                 'Hz' in line or '해상도' in line or '밝기' in line or 'CPU' in line or '램' in line or
                                 '그래픽' in line or '배터리' in line or '용도' in line)):
                                spec_parts.append(line)
                        
                        if spec_parts:
                            # 중복 제거 및 정리
                            unique_specs = []
                            seen = set()
                            for spec in spec_parts:
                                if spec not in seen and len(spec) > 5:
                                    seen.add(spec)
                                    unique_specs.append(spec)
                            if unique_specs:
                                specs = " / ".join(unique_specs[:30])  # 최대 30개까지만
                    except:
                        pass
                
                # 여전히 스펙을 찾지 못한 경우 리스트 항목들 찾기
                if not specs:
                    try:
                        spec_items = item.find_elements(By.CSS_SELECTOR, 
                            ".spec_list li, .spec_info li, .prod_spec li, dl.spec_list dt, dl.spec_list dd, .summary_info li")
                        if spec_items:
                            spec_parts = []
                            for spec_item in spec_items:
                                spec_text = spec_item.text.strip()
                                if (spec_text and len(spec_text) > 3 and 
                                    '원' not in spec_text and
                                    '배송' not in spec_text and
                                    '할인' not in spec_text):
                                    spec_parts.append(spec_text)
                            if spec_parts:
                                specs = " / ".join(spec_parts[:20])
                    except:
                        pass
                        
            except Exception as e:
                pass
            
            # 필수 정보가 없는 경우 제외
            if not product_name or not price:
                return None
            
            return {
                '상품명': product_name,
                '가격': price,
                '별점': rating if rating else '',
                '리뷰 수': review_count if review_count else '',
                '스펙': specs if specs else '',
                '상품 상세 URL': product_url if product_url else ''
            }
            
        except Exception as e:
            return None
    
    def extract_specs_from_detail_page(self, detail_url):
        """상품 상세 페이지에서 스펙 정보 추출"""
        specs_list = []
        
        try:
            # 현재 창 저장
            original_window = self.driver.current_window_handle
            
            # 새 탭에서 상세 페이지 열기
            self.driver.execute_script("window.open('');")
            self.driver.switch_to.window(self.driver.window_handles[-1])
            
            # 상세 페이지 로드
            self.driver.get(detail_url)
            time.sleep(random.uniform(2, 4))
            
            # 스펙 정보 찾기 (다나와 상세 페이지 구조)
            try:
                # 페이지 로드 대기
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # 다나와 상세 페이지의 스펙 섹션 찾기 (더 포괄적인 선택자)
                spec_selectors = [
                    ".spec_list li",
                    ".spec_item",
                    ".prod_spec li",
                    ".spec_info li",
                    "table.spec_table tr",
                    ".summary_info li",
                    ".prod_summary_info li",
                    "[class*='spec'] li",
                    ".detail_spec tr",
                    ".prod_spec_list li",
                    ".spec_table tbody tr",
                    ".spec_detail li",
                    ".prod_info_spec li"
                ]
                
                for selector in spec_selectors:
                    try:
                        spec_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if spec_elements:
                            for spec_elem in spec_elements:
                                try:
                                    spec_text = spec_elem.text.strip()
                                    # 의미있는 스펙만 추출 (키:값 형식 또는 의미있는 텍스트)
                                    if (spec_text and len(spec_text) > 3 and 
                                        not spec_text.startswith('http') and
                                        not spec_text.startswith('javascript') and
                                        ('/' in spec_text or ':' in spec_text or len(spec_text) > 15)):
                                        specs_list.append(spec_text)
                                except:
                                    continue
                            if len(specs_list) > 5:  # 충분한 스펙을 찾았으면 중단
                                break
                    except:
                        continue
                
                # 스펙이 없으면 요약 정보에서 찾기
                if not specs_list:
                    try:
                        summary_selectors = [
                            ".prod_summary",
                            ".summary_spec",
                            ".main_spec",
                            ".prod_info_summary",
                            ".prod_summary_info",
                            ".summary_info"
                        ]
                        for selector in summary_selectors:
                            try:
                                summary_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                                summary_text = summary_elem.text.strip()
                                if summary_text and len(summary_text) > 20:
                                    # 줄바꿈이나 구분자로 분리
                                    lines = summary_text.replace(' / ', '\n').replace('/', '\n').split('\n')
                                    for line in lines:
                                        line = line.strip()
                                        if line and len(line) > 3 and not line.startswith('http'):
                                            specs_list.append(line)
                                    if specs_list:
                                        break
                            except:
                                continue
                    except:
                        pass
                
            except Exception as e:
                pass
            
            # 탭 닫고 원래 창으로 돌아가기
            self.driver.close()
            self.driver.switch_to.window(original_window)
            
            # 스펙 정보를 문자열로 결합
            if specs_list:
                # 중복 제거 및 정리
                unique_specs = []
                seen = set()
                for spec in specs_list:
                    spec_clean = spec.strip()
                    if spec_clean and spec_clean not in seen:
                        seen.add(spec_clean)
                        unique_specs.append(spec_clean)
                
                return " / ".join(unique_specs[:50])  # 최대 50개까지만
            
        except Exception as e:
            # 오류 발생 시 원래 창으로 돌아가기
            try:
                if len(self.driver.window_handles) > 1:
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])
            except:
                pass
        
        return ""
    
    def crawl(self, keywords, items_per_keyword=70):
        """메인 크롤링 함수"""
        all_products = []
        
        for keyword in keywords:
            products = self.search_products(keyword, items_per_keyword)
            all_products.extend(products)
            self.wait_random()
        
        return all_products
    
    def save_to_csv(self, products, filename='electronics_data.csv'):
        """수집된 데이터를 CSV 파일로 저장"""
        if not products:
            print("저장할 데이터가 없습니다.")
            return
        
        fieldnames = ['상품명', '가격', '별점', '리뷰 수', '스펙', '상품 상세 URL']
        
        with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(products)
        
        print(f"\n데이터 저장 완료: {filename} ({len(products)}개 항목)")
    
    def close(self):
        """드라이버 종료"""
        if self.driver:
            self.driver.quit()
            print("브라우저 종료 완료")


def main():
    """메인 실행 함수"""
    crawler = None
    
    try:
        # 크롤러 초기화
        crawler = DanawaCrawler()
        
        # 수집할 키워드 및 개수
        keywords = ['노트북', '데스크탑']
        items_per_keyword = 100
        
        print("=" * 50)
        print("다나와 전자제품 크롤러 시작")
        print("=" * 50)
        print(f"키워드: {keywords}")
        print(f"키워드당 수집 개수: {items_per_keyword}개")
        print(f"예상 총 수집 개수: {len(keywords) * items_per_keyword}개")
        print("=" * 50)
        
        # 크롤링 실행
        all_products = crawler.crawl(keywords, items_per_keyword)
        
        # CSV 파일로 저장
        if all_products:
            crawler.save_to_csv(all_products)
            print(f"\n총 {len(all_products)}개의 상품 데이터를 수집했습니다.")
        else:
            print("\n수집된 데이터가 없습니다.")
        
    except KeyboardInterrupt:
        print("\n\n사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n오류 발생: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if crawler:
            crawler.close()


if __name__ == "__main__":
    main()
