import streamlit as st
import pandas as pd
import google.generativeai as genai
from langchain_community.tools.tavily_search import TavilySearchResults
import re
from typing import List, Dict, Optional
import json
import os
from dotenv import load_dotenv
import urllib.parse

# .env 파일에서 환경 변수 로드
load_dotenv()

# API 키 설정 (우선순위: 환경 변수 > .env 파일 > 직접 입력)
# 방법 1: 환경 변수에서 읽기 (export GEMINI_API_KEY=...)
# 방법 2: .env 파일에 저장 (GEMINI_API_KEY=...)
# 방법 3: 아래 주석을 해제하고 직접 입력
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')  # 환경 변수 또는 .env에서 읽기
TAVILY_API_KEY = os.getenv('TAVILY_API_KEY', '')  # 환경 변수 또는 .env에서 읽기
GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')  # 기본 모델

# 방법 3: 환경 변수가 없으면 여기에 직접 입력 (보안 주의!)
# GEMINI_API_KEY = 'your-gemini-api-key-here'
# TAVILY_API_KEY = 'your-tavily-api-key-here'

# 페이지 설정
st.set_page_config(
    page_title="테크 전문 쇼핑 가이드 챗봇",
    page_icon="💻",
    layout="centered"
)

# 기본 CSS 스타일
st.markdown("""
<style>
    /* 버튼 스타일 */
    .stButton>button {
        background-color: #6336FF;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        border: none;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #5229E6;
        color: white;
    }
    
    /* 제품 카드 */
    .product-card {
        background-color: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(99, 54, 255, 0.1);
        border: 1px solid #e0e0e0;
    }
    .product-name {
        font-size: 1.2rem;
        font-weight: 700;
        color: #1a1a1a;
        margin-bottom: 0.5rem;
    }
    .product-price {
        font-size: 1.5rem;
        font-weight: 700;
        color: #6336FF;
        margin: 0.5rem 0;
    }
    .product-spec {
        color: #666;
        font-size: 0.9rem;
        line-height: 1.6;
        margin: 1rem 0;
    }
    
    /* 채팅 메시지 */
    .chat-message {
        padding: 0.75rem 1rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        max-width: 85%;
        word-wrap: break-word;
    }
    .user-message {
        background-color: #6336FF;
        color: white;
        margin-left: auto;
        margin-right: 0;
    }
    .bot-message {
        background-color: #f0f0f0;
        color: #1a1a1a;
        margin-left: 0;
        margin-right: auto;
    }
</style>
""", unsafe_allow_html=True)

# 상품 데이터 자동 로드 함수
def load_products_data():
    """상품 데이터를 CSV 파일에서 자동으로 로드"""
    try:
        if os.path.exists('electronics_data.csv'):
            df = pd.read_csv('electronics_data.csv', encoding='utf-8-sig')
            # 컬럼명 정리 (가격 -> 최저가, 스펙 -> 상세스펙)
            column_mapping = {}
            if '가격' in df.columns:
                column_mapping['가격'] = '최저가'
            if '스펙' in df.columns:
                column_mapping['스펙'] = '상세스펙'
            if '상품 상세 URL' in df.columns:
                column_mapping['상품 상세 URL'] = 'URL'
            
            if column_mapping:
                df = df.rename(columns=column_mapping)
            
            # 최저가가 없는 경우 가격 컬럼 확인
            if '최저가' not in df.columns and '가격' in df.columns:
                df['최저가'] = df['가격']
            
            return df
        else:
            return None
    except Exception as e:
        return None

# 세션 상태 초기화
if 'conversation_state' not in st.session_state:
    st.session_state.conversation_state = 'idle'  # idle, usage_asked, software_asked, budget_asked, weight_asked, portable_asked, products_recommended
if 'user_intent' not in st.session_state:
    st.session_state.user_intent = None  # '노트북', 'PC', '데스크탑' 등
if 'user_usage' not in st.session_state:
    st.session_state.user_usage = None  # '게임용', '작업용', '사무용' 등
if 'user_software' not in st.session_state:
    st.session_state.user_software = None  # '롤', '프리미어 프로' 등
if 'user_budget' not in st.session_state:
    st.session_state.user_budget = None  # 예산 (숫자)
if 'user_weight_preference' not in st.session_state:
    st.session_state.user_weight_preference = None  # '가벼운', '보통', '무거워도됨' 등
if 'user_portable_need' not in st.session_state:
    st.session_state.user_portable_need = None  # True/False
if 'recommended_products' not in st.session_state:
    st.session_state.recommended_products = []
if 'spec_info' not in st.session_state:
    st.session_state.spec_info = None  # 시스템 요구사항 정보 저장
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'products_df' not in st.session_state:
    # 앱 시작 시 상품 데이터 자동 로드
    st.session_state.products_df = load_products_data()
if 'gemini_model' not in st.session_state:
    st.session_state.gemini_model = 'gemini-2.5-flash'

# API 키를 세션 상태에 저장
if 'gemini_api_key' not in st.session_state:
    st.session_state.gemini_api_key = GEMINI_API_KEY
if 'tavily_api_key' not in st.session_state:
    st.session_state.tavily_api_key = TAVILY_API_KEY
if 'gemini_model' not in st.session_state:
    st.session_state.gemini_model = GEMINI_MODEL

# 함수 정의 (사이드바에서 사용하기 위해 먼저 정의)
def get_available_models(gemini_api_key: str) -> List[str]:
    """사용 가능한 Gemini 모델 목록 가져오기"""
    try:
        genai.configure(api_key=gemini_api_key)
        models = genai.list_models()
        available = []
        for model in models:
            if 'generateContent' in model.supported_generation_methods:
                model_name = model.name.replace('models/', '')
                available.append(model_name)
        return available
    except Exception as e:
        return ['gemini-2.5-flash', 'gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']

def initialize_gemini_model(gemini_api_key: str, preferred_model: str = 'gemini-2.5-flash'):
    """Gemini 모델 초기화 (여러 방법 시도)"""
    if not gemini_api_key:
        return None, "API 키가 설정되지 않았습니다."
    
    genai.configure(api_key=gemini_api_key)
    
    # 시도할 모델 이름 목록 (우선순위 순)
    model_names_to_try = [
        preferred_model,
        f'models/{preferred_model}',
        'gemini-2.5-flash',
        'models/gemini-2.5-flash',
        'gemini-1.5-flash',
        'models/gemini-1.5-flash',
        'gemini-1.5-pro',
        'models/gemini-1.5-pro',
        'gemini-pro',
        'models/gemini-pro',
    ]
    
    # 중복 제거
    model_names_to_try = list(dict.fromkeys(model_names_to_try))
    
    last_error = None
    for model_name in model_names_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            return model, None
        except Exception as e:
            last_error = e
            continue
    
    # 모든 모델 시도 실패 시, 사용 가능한 모델 목록 확인
    try:
        available_models = get_available_models(gemini_api_key)
        if available_models:
            # 사용 가능한 첫 번째 모델 시도
            for available_model in available_models:
                try:
                    model = genai.GenerativeModel(available_model)
                    return model, None
                except:
                    continue
    except:
        pass
    
    error_msg = f"모델을 초기화할 수 없습니다. 시도한 모델: {', '.join(model_names_to_try[:3])}... 마지막 오류: {str(last_error)}"
    return None, error_msg

# 사이드바 - 설정 (챗봇 위젯 모드에서는 숨김)
# with st.sidebar:
if False:  # 사이드바 비활성화
    st.header("⚙️ 설정")
    
    # API 키 상태 표시
    if st.session_state.gemini_api_key:
        st.success("✅ Gemini API 키 설정됨")
        
        # 모델 테스트 버튼
        if st.button("🔍 Gemini 모델 테스트"):
            with st.spinner("모델 연결 테스트 중..."):
                # 사용 가능한 모델 목록 확인
                try:
                    available_models = get_available_models(st.session_state.gemini_api_key)
                    if available_models:
                        st.info(f"📋 사용 가능한 모델: {', '.join(available_models[:5])}")
                except:
                    pass
                
                model, error = initialize_gemini_model(
                    st.session_state.gemini_api_key,
                    st.session_state.gemini_model
                )
                if model:
                    try:
                        test_response = model.generate_content("안녕하세요")
                        st.success(f"✅ 모델 연결 성공! (응답: {test_response.text[:50]}...)")
                    except Exception as e:
                        st.error(f"❌ 모델 테스트 실패: {str(e)}")
                else:
                    st.error(f"❌ 모델 초기화 실패: {error}")
    else:
        st.error("⚠️ Gemini API 키가 설정되지 않았습니다. 환경 변수 또는 코드에서 설정해주세요.")
    
    if st.session_state.tavily_api_key:
        st.success("✅ Tavily API 키 설정됨")
    else:
        st.error("⚠️ Tavily API 키가 설정되지 않았습니다. 환경 변수 또는 코드에서 설정해주세요.")
    
    st.divider()
    
    # CSV 파일 로드
    if st.button("📊 상품 데이터 로드"):
        load_status = st.empty()
        with load_status:
            st.info("📂 **데이터를 로드하는 중입니다...**")
        try:
            df = pd.read_csv('electronics_data.csv', encoding='utf-8-sig')
            # 컬럼명 정리 (가격 -> 최저가, 스펙 -> 상세스펙)
            column_mapping = {}
            if '가격' in df.columns:
                column_mapping['가격'] = '최저가'
            if '스펙' in df.columns:
                column_mapping['스펙'] = '상세스펙'
            if '상품 상세 URL' in df.columns:
                column_mapping['상품 상세 URL'] = 'URL'
            
            if column_mapping:
                df = df.rename(columns=column_mapping)
            
            # 최저가가 없는 경우 가격 컬럼 확인
            if '최저가' not in df.columns and '가격' in df.columns:
                df['최저가'] = df['가격']
            
            st.session_state.products_df = df
            load_status.empty()
            st.success(f"✅ {len(df)}개의 상품 데이터가 로드되었습니다!")
        except Exception as e:
            load_status.empty()
            st.error(f"데이터 로드 실패: {e}")

def format_price(price):
    """가격을 원 단위로 포맷팅 (3자리마다 콤마)"""
    if pd.isna(price) or price == '':
        return "가격 정보 없음"
    try:
        price_int = int(float(str(price).replace(',', '')))
        return f"{price_int:,}원"
    except:
        return str(price)

def escape_html(text: str) -> str:
    """HTML 특수 문자를 이스케이프"""
    if not text:
        return ""
    text = str(text)
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&#x27;')
    return text

def generate_products_html(products: List[Dict], product_descriptions: Dict = None, user_software: str = None, user_usage: str = None) -> str:
    """제품 목록을 HTML로 변환"""
    products_html = '<div style="margin-top: 1rem;"><h3 style="color: #6336FF; margin-bottom: 1rem;">🎯 추천 상품</h3>'
    
    for i, product in enumerate(products, 1):
        # 제품명과 가격 이스케이프
        product_name = escape_html(product.get("상품명", ""))
        product_price = format_price(product.get("최저가", ""))
        
        products_html += f'<div class="product-card" style="margin-bottom: 1.5rem;">'
        products_html += f'<div class="product-name">{i}. {product_name}</div>'
        products_html += f'<div class="product-price">{product_price}</div>'
        
        # 상품 설명
        if product_descriptions and i-1 in product_descriptions and product_descriptions[i-1]:
            desc = escape_html(product_descriptions[i-1])
            products_html += f'<div class="product-spec" style="margin: 1rem 0; padding: 1rem; background-color: #f8f9fa; border-radius: 8px; border-left: 4px solid #6336FF;">💡 <strong>추천 이유:</strong><br>{desc}</div>'
        else:
            # 스펙 기반 간단한 설명
            spec_text = str(product.get('상세스펙', ''))
            if spec_text:
                key_features = []
                if '외장그래픽' in spec_text or 'RTX' in spec_text or 'GTX' in spec_text:
                    key_features.append("강력한 외장 그래픽카드")
                if '16GB' in spec_text or '32GB' in spec_text:
                    ram_match = re.search(r'(\d+)\s*GB', spec_text)
                    if ram_match:
                        key_features.append(f"{ram_match.group(1)}GB RAM")
                if 'SSD' in spec_text or 'M.2' in spec_text:
                    key_features.append("고속 SSD")
                
                if key_features:
                    simple_desc = f"이 제품은 {', '.join(key_features)}를 갖추고 있어 {user_software or user_usage or '작업'}에 적합합니다."
                    simple_desc = escape_html(simple_desc)
                    products_html += f'<div class="product-spec" style="margin: 1rem 0; padding: 1rem; background-color: #f8f9fa; border-radius: 8px; border-left: 4px solid #6336FF;">💡 <strong>추천 이유:</strong><br>{simple_desc}</div>'
        
        # 핵심 스펙
        spec_text = str(product.get('상세스펙', ''))[:200]
        if spec_text:
            spec_text_escaped = escape_html(spec_text)
            products_html += f'<div class="product-spec">📋 핵심 스펙: {spec_text_escaped}...</div>'
        
        # 별점 및 리뷰 수
        if product.get('별점') and product.get('리뷰 수'):
            rating = escape_html(str(product.get('별점', '')))
            review_count = escape_html(str(product.get('리뷰 수', '')))
            products_html += f'<div style="margin: 0.5rem 0; color: #666;">⭐ {rating}점 | 💬 리뷰 {review_count}개</div>'
        
        # 다나와 링크 (CSV 파일의 실제 URL 사용 - 항상 버튼 표시)
        product_url = product.get('URL', '') or product.get('상품 상세 URL', '')
        url_str = None
        
        if product_url and str(product_url).strip() and str(product_url) != 'nan':
            # URL이 유효한지 확인 (http 또는 https로 시작)
            url_str = str(product_url).strip()
            if not url_str.startswith('http'):
                # 상대 경로인 경우 다나와 도메인 추가
                if url_str.startswith('/'):
                    url_str = 'https://www.danawa.com' + url_str
                elif 'danawa.com' not in url_str:
                    url_str = 'https://www.danawa.com/' + url_str
        
        # URL이 없으면 제품명으로 다나와 검색 페이지로 연결
        if not url_str:
            product_name_for_search = product.get("상품명", "")
            # 제품명을 URL 인코딩하여 검색 URL 생성
            encoded_name = urllib.parse.quote(product_name_for_search)
            url_str = f'https://search.danawa.com/dsearch.php?query={encoded_name}'
        
        url_escaped = escape_html(url_str)
        products_html += f'<a href="{url_escaped}" target="_blank" style="display: inline-block; margin-top: 0.5rem; padding: 0.5rem 1rem; background-color: #6336FF; color: white; text-decoration: none; border-radius: 8px; font-weight: 600;">🔗 다나와 최저가 확인</a>'
        
        products_html += '</div>'
    
    products_html += '</div>'
    return products_html

def detect_intent(user_input: str) -> Optional[str]:
    """사용자 입력에서 의도 감지"""
    keywords = {
        '노트북': ['노트북', '랩탑', 'laptop', 'notebook'],
        'PC': ['pc', '컴퓨터', '데스크탑', 'desktop', '데스크톱'],
        '데스크탑': ['데스크탑', 'desktop', '데스크톱', 'pc', '컴퓨터']
    }
    
    user_input_lower = user_input.lower()
    for intent, keyword_list in keywords.items():
        for keyword in keyword_list:
            if keyword in user_input_lower:
                return intent
    return None

def search_system_requirements(software_name: str, tavily_api_key: str) -> Dict:
    """Tavily를 사용하여 소프트웨어의 시스템 요구사항 검색"""
    try:
        search = TavilySearchResults(api_key=tavily_api_key, max_results=3)
        query = f"{software_name} 시스템 요구사항 권장 사양 CPU RAM GPU"
        results = search.invoke(query)
        
        # 검색 결과에서 사양 정보 추출
        spec_info = {
            'cpu': None,
            'ram': None,
            'gpu': None,
            'storage': None,
            'description': ''
        }
        
        for result in results:
            content = result.get('content', '')
            spec_info['description'] += content + " "
            
            # CPU 정보 추출
            cpu_patterns = [
                r'(?:CPU|프로세서)[:\s]*([A-Za-z0-9\s\-]+?)(?:GHz|코어|core|RAM|GPU|$)',
                r'(인텔|AMD|Intel|라이젠|코어|Core)[\s\w\-]+(?:GHz|코어|core)',
            ]
            for pattern in cpu_patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match and not spec_info['cpu']:
                    spec_info['cpu'] = match.group(0)[:100]
            
            # RAM 정보 추출
            ram_patterns = [
                r'(\d+)\s*GB\s*(?:RAM|램|메모리)',
                r'RAM[:\s]*(\d+)\s*GB',
            ]
            for pattern in ram_patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match and not spec_info['ram']:
                    spec_info['ram'] = int(match.group(1))
            
            # GPU 정보 추출
            gpu_patterns = [
                r'(?:GPU|그래픽|비디오)[:\s]*([A-Za-z0-9\s\-]+?)(?:RAM|GB|$|메모리)',
                r'(RTX|GTX|Radeon|NVIDIA|AMD)[\s\w\d]+',
            ]
            for pattern in gpu_patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match and not spec_info['gpu']:
                    spec_info['gpu'] = match.group(0)[:100]
        
        return spec_info
    except Exception as e:
        st.error(f"웹 검색 오류: {e}")
        return {}

def extract_cpu_from_spec(spec_text: str) -> Optional[Dict]:
    """스펙 텍스트에서 CPU 정보 추출"""
    spec_lower = spec_text.lower()
    cpu_info = {'brand': None, 'model': None, 'generation': None, 'score': 0}
    
    # 인텔 CPU 추출
    intel_patterns = [
        r'(?:인텔|intel)[\s/]*코어[\s/]*(?:i|울트라|ultra)?[\s/]*(\d+)[\s/]*(?:세대|gen)?[\s/]*(?:i|울트라|ultra)?[\s/]*(\d+)[\s/]*([a-z0-9]+)?',
        r'코어[\s/]*(?:i|울트라|ultra)?[\s/]*(\d+)[\s/]*(?:세대|gen)?[\s/]*(?:i|울트라|ultra)?[\s/]*(\d+)[\s/]*([a-z0-9]+)?',
        r'i(\d+)[\s/]*-[\s/]*(\d+)[\s/]*세대',
        r'코어[\s/]*울트라[\s/]*(\d+)[\s/]*\([^)]*\)',
    ]
    for pattern in intel_patterns:
        match = re.search(pattern, spec_lower, re.IGNORECASE)
        if match:
            cpu_info['brand'] = 'intel'
            if len(match.groups()) >= 2:
                cpu_info['generation'] = int(match.group(1)) if match.group(1).isdigit() else None
                cpu_info['model'] = match.group(2) if len(match.groups()) > 1 else None
            break
    
    # AMD CPU 추출
    amd_patterns = [
        r'(?:amd|라이젠|ryzen)[\s/]*(\d+)[\s/]*(?:zen[\s/]*(\d+))?[\s/]*([a-z0-9]+)?',
        r'라이젠[\s/]*(\d+)[\s/]*\([^)]*\)',
    ]
    for pattern in amd_patterns:
        match = re.search(pattern, spec_lower, re.IGNORECASE)
        if match:
            cpu_info['brand'] = 'amd'
            if match.group(1).isdigit():
                cpu_info['generation'] = int(match.group(1))
            break
    
    # CPU 성능 점수 계산 (세대와 모델 번호 기반)
    if cpu_info['generation']:
        cpu_info['score'] = cpu_info['generation'] * 10
        if cpu_info['model'] and cpu_info['model'].isdigit():
            cpu_info['score'] += int(cpu_info['model'])
    
    return cpu_info if cpu_info['brand'] else None

def extract_gpu_from_spec(spec_text: str) -> Optional[Dict]:
    """스펙 텍스트에서 GPU 정보 추출"""
    spec_lower = spec_text.lower()
    gpu_info = {'type': None, 'model': None, 'score': 0}
    
    # RTX 추출
    rtx_match = re.search(r'rtx[\s/]*(\d{4,5})', spec_lower, re.IGNORECASE)
    if rtx_match:
        gpu_info['type'] = 'rtx'
        gpu_info['model'] = int(rtx_match.group(1))
        gpu_info['score'] = 1000 + gpu_info['model']  # RTX는 높은 점수
        return gpu_info
    
    # GTX 추출
    gtx_match = re.search(r'gtx[\s/]*(\d{3,4})', spec_lower, re.IGNORECASE)
    if gtx_match:
        gpu_info['type'] = 'gtx'
        gpu_info['model'] = int(gtx_match.group(1))
        gpu_info['score'] = 500 + gpu_info['model']  # GTX는 중간 점수
        return gpu_info
    
    # Radeon RX 추출
    rx_match = re.search(r'rx[\s/]*(\d{4})', spec_lower, re.IGNORECASE)
    if rx_match:
        gpu_info['type'] = 'radeon'
        gpu_info['model'] = int(rx_match.group(1))
        gpu_info['score'] = 800 + gpu_info['model']
        return gpu_info
    
    # 외장 그래픽 여부만 확인
    if '외장그래픽' in spec_lower:
        gpu_info['type'] = 'external'
        gpu_info['score'] = 100
        return gpu_info
    
    return None

def extract_ram_from_spec(spec_text: str) -> Optional[int]:
    """스펙 텍스트에서 RAM 정보 추출 (GB)"""
    ram_matches = re.findall(r'(\d+)\s*gb', spec_text, re.IGNORECASE)
    if ram_matches:
        # 가장 큰 RAM 값 반환
        return max([int(m) for m in ram_matches])
    return None

def parse_required_cpu(cpu_text: str) -> Optional[Dict]:
    """요구사항 CPU 텍스트 파싱"""
    if not cpu_text:
        return None
    
    cpu_lower = cpu_text.lower()
    cpu_info = {'brand': None, 'model': None, 'generation': None, 'score': 0}
    
    # 인텔 CPU 파싱
    intel_match = re.search(r'(?:intel|인텔)[\s/]*core[\s/]*(?:i|i-)?[\s/]*(\d+)[\s/]*-[\s/]*(\d+)([a-z]+)?', cpu_lower, re.IGNORECASE)
    if intel_match:
        cpu_info['brand'] = 'intel'
        if intel_match.group(1).isdigit():
            cpu_info['generation'] = int(intel_match.group(1))
        if intel_match.group(2).isdigit():
            cpu_info['model'] = int(intel_match.group(2))
        if cpu_info['generation']:
            cpu_info['score'] = cpu_info['generation'] * 10
            if cpu_info['model']:
                cpu_info['score'] += cpu_info['model']
        return cpu_info
    
    # AMD CPU 파싱
    amd_match = re.search(r'(?:amd|라이젠|ryzen)[\s/]*(\d+)[\s/]*(\d{4})?', cpu_lower, re.IGNORECASE)
    if amd_match:
        cpu_info['brand'] = 'amd'
        if amd_match.group(1).isdigit():
            cpu_info['generation'] = int(amd_match.group(1))
        if cpu_info['generation']:
            cpu_info['score'] = cpu_info['generation'] * 10
        return cpu_info
    
    return None

def parse_required_gpu(gpu_text: str) -> Optional[Dict]:
    """요구사항 GPU 텍스트 파싱"""
    if not gpu_text:
        return None
    
    gpu_lower = gpu_text.lower()
    gpu_info = {'type': None, 'model': None, 'score': 0}
    
    # RTX 추출
    rtx_match = re.search(r'rtx[\s/]*(\d{4,5})', gpu_lower, re.IGNORECASE)
    if rtx_match:
        gpu_info['type'] = 'rtx'
        gpu_info['model'] = int(rtx_match.group(1))
        gpu_info['score'] = 1000 + gpu_info['model']
        return gpu_info
    
    # GTX 추출
    gtx_match = re.search(r'gtx[\s/]*(\d{3,4})', gpu_lower, re.IGNORECASE)
    if gtx_match:
        gpu_info['type'] = 'gtx'
        gpu_info['model'] = int(gtx_match.group(1))
        gpu_info['score'] = 500 + gpu_info['model']
        return gpu_info
    
    # Radeon 추출
    rx_match = re.search(r'(?:radeon|rx)[\s/]*(\d{4})', gpu_lower, re.IGNORECASE)
    if rx_match:
        gpu_info['type'] = 'radeon'
        gpu_info['model'] = int(rx_match.group(1))
        gpu_info['score'] = 800 + gpu_info['model']
        return gpu_info
    
    return None

def match_products_by_spec(spec_info: Dict, products_df: pd.DataFrame, product_type: str, 
                          budget: Optional[int] = None, weight_preference: Optional[str] = None, 
                          portable_need: Optional[bool] = None) -> List[Dict]:
    """시스템 사양에 맞는 상품 필터링 - 요구사항과 실제 스펙을 비교"""
    if products_df is None or len(products_df) == 0:
        return []
    
    # 제품 타입 필터링 (더 엄격하게)
    if product_type == '노트북':
        # 노트북만 포함하고, 데스크탑/PC는 제외
        filtered_df = products_df[
            products_df['상품명'].str.contains('노트북|랩탑|laptop', case=False, na=False) &
            ~products_df['상품명'].str.contains('데스크탑|PC|컴퓨터', case=False, na=False)
        ]
    elif product_type in ['PC', '데스크탑']:
        # 데스크탑/PC만 포함하고, 노트북은 제외
        filtered_df = products_df[
            (products_df['상품명'].str.contains('데스크탑|PC|컴퓨터', case=False, na=False)) &
            ~products_df['상품명'].str.contains('노트북|랩탑|laptop', case=False, na=False)
        ]
    else:
        filtered_df = products_df
    
    if len(filtered_df) == 0:
        return []
    
    # 요구사항 파싱
    required_cpu = parse_required_cpu(spec_info.get('cpu', ''))
    required_ram = spec_info.get('ram')
    required_gpu = parse_required_gpu(spec_info.get('gpu', ''))
    
    # 스펙 매칭 점수 계산
    scored_products = []
    
    for idx, row in filtered_df.iterrows():
        score = 0
        spec_text = str(row.get('상세스펙', row.get('스펙', '')))
        product_name = str(row.get('상품명', ''))
        
        # 제품 스펙 추출
        product_cpu = extract_cpu_from_spec(spec_text)
        product_ram = extract_ram_from_spec(spec_text)
        product_gpu = extract_gpu_from_spec(spec_text)
        
        # CPU 매칭 (요구사항과 비교)
        if required_cpu and product_cpu:
            if required_cpu['brand'] == product_cpu['brand']:
                score += 20  # 같은 브랜드
                # 세대와 모델 비교
                if product_cpu.get('generation') and required_cpu.get('generation'):
                    if product_cpu['generation'] >= required_cpu['generation']:
                        score += 30  # 요구사항 이상의 세대
                        # 모델 번호 비교
                        if product_cpu.get('model') and required_cpu.get('model'):
                            if product_cpu['model'] >= required_cpu['model']:
                                score += 20  # 요구사항 이상의 모델
                            else:
                                score += 10  # 모델은 낮지만 세대는 높음
                    else:
                        score += 5  # 세대가 낮지만 같은 브랜드
            else:
                # 다른 브랜드지만 성능 점수로 비교
                if product_cpu.get('score', 0) >= required_cpu.get('score', 0):
                    score += 15
        elif required_cpu:
            # CPU 요구사항은 있지만 제품 CPU를 못 찾은 경우, 키워드 매칭
            cpu_keywords = ['인텔', 'amd', '라이젠', '코어', 'intel', 'ryzen', 'core']
            for keyword in cpu_keywords:
                if keyword.lower() in required_cpu.get('brand', '').lower() and keyword.lower() in spec_text.lower():
                    score += 5
                    break
        
        # RAM 매칭
        if required_ram and product_ram:
            if product_ram >= required_ram:
                score += 30  # 요구사항 이상
                if product_ram >= required_ram * 1.5:
                    score += 10  # 여유 있음
            else:
                score += 5  # 부족하지만 있음
        
        # GPU 매칭 (가장 중요)
        if required_gpu and product_gpu:
            if required_gpu['type'] == product_gpu['type']:
                score += 40  # 같은 타입 (RTX, GTX 등)
                if product_gpu.get('model') and required_gpu.get('model'):
                    if product_gpu['model'] >= required_gpu['model']:
                        score += 30  # 요구사항 이상의 모델
                    else:
                        score += 10  # 모델은 낮지만 같은 타입
            else:
                # 다른 타입이지만 성능 점수로 비교
                if product_gpu.get('score', 0) >= required_gpu.get('score', 0):
                    score += 20
        elif required_gpu:
            # GPU 요구사항은 있지만 제품 GPU를 못 찾은 경우
            if required_gpu['type'] == 'rtx' and 'rtx' in spec_text.lower():
                score += 15
            elif required_gpu['type'] == 'gtx' and 'gtx' in spec_text.lower():
                score += 15
            elif '외장그래픽' in spec_text.lower():
                score += 10
        elif product_gpu and product_gpu['type'] in ['rtx', 'gtx', 'radeon']:
            # GPU 요구사항은 없지만 외장 그래픽이 있는 경우 (게임용)
            if st.session_state.get('user_usage') == '게임용':
                score += 20
        
        # 게임용/작업용인 경우 외장 그래픽 필수 체크
        user_usage = st.session_state.get('user_usage')
        if user_usage in ['게임용', '작업용']:
            if product_gpu and product_gpu['type'] in ['rtx', 'gtx', 'radeon', 'external']:
                score += 15  # 외장 그래픽 보너스
            elif '내장그래픽' in spec_text.lower() and '외장그래픽' not in spec_text.lower():
                # 내장 그래픽만 있으면 매우 큰 감점 (거의 제외)
                score -= 100  # 내장 그래픽만 있으면 거의 제외
        
        # 예산 필터링 및 점수 조정
        if budget:
            try:
                product_price = int(float(str(row.get('최저가', row.get('가격', '0'))).replace(',', '')))
                if product_price <= budget:
                    # 예산 내면 가산점 (예산에 가까울수록 높은 점수)
                    price_ratio = product_price / budget
                    if price_ratio >= 0.9:
                        score += 10  # 예산의 90% 이상 사용
                    elif price_ratio >= 0.7:
                        score += 15  # 예산의 70-90%
                    elif price_ratio >= 0.5:
                        score += 20  # 예산의 50-70% (가성비 좋음)
                    else:
                        score += 10  # 예산의 50% 미만
                else:
                    # 예산 초과시 감점
                    over_ratio = (product_price - budget) / budget
                    if over_ratio <= 0.1:
                        score -= 5  # 10% 이하 초과
                    elif over_ratio <= 0.2:
                        score -= 15  # 20% 이하 초과
                    else:
                        score -= 30  # 20% 이상 초과
            except:
                pass
        
        # 무게 필터링 (노트북만)
        if weight_preference and product_type == '노트북':
            weight_matches = re.findall(r'(\d+\.?\d*)\s*kg', spec_text, re.IGNORECASE)
            if weight_matches:
                try:
                    product_weight = float(weight_matches[0])
                    if weight_preference == '가벼운':
                        if product_weight <= 1.5:
                            score += 20
                        elif product_weight <= 2.0:
                            score += 10
                        else:
                            score -= 10
                    elif weight_preference == '보통':
                        if 1.5 <= product_weight <= 2.5:
                            score += 10
                    elif weight_preference == '무거워도됨':
                        score += 5  # 무게 무관
                except:
                    pass
        
        # 휴대용 필요 여부 (노트북만)
        if portable_need is not None and product_type == '노트북':
            if portable_need:
                # 가벼운 제품 선호
                weight_matches = re.findall(r'(\d+\.?\d*)\s*kg', spec_text, re.IGNORECASE)
                if weight_matches:
                    try:
                        product_weight = float(weight_matches[0])
                        if product_weight <= 1.5:
                            score += 15
                        elif product_weight <= 2.0:
                            score += 5
                    except:
                        pass
            else:
                # 휴대용 불필요하면 무게 무관
                score += 5
        
        scored_products.append({
            '상품명': product_name,
            '최저가': row.get('최저가', row.get('가격', '')),
            '상세스펙': row.get('상세스펙', row.get('스펙', '')),
            'URL': row.get('URL', row.get('상품 상세 URL', '')),
            '별점': row.get('별점', ''),
            '리뷰 수': row.get('리뷰 수', ''),
            'score': score
        })
    
    # 점수 순으로 정렬
    scored_products.sort(key=lambda x: x['score'], reverse=True)
    
    # 게임용/작업용인 경우 내장 그래픽만 있는 제품 제외
    user_usage = st.session_state.get('user_usage')
    if user_usage in ['게임용', '작업용']:
        valid_products = []
        for p in scored_products:
            spec_text = str(p.get('상세스펙', '')).lower()
            # 내장 그래픽만 있고 외장 그래픽이 없는 제품 제외
            if '내장그래픽' in spec_text and '외장그래픽' not in spec_text:
                continue
            # 외장 그래픽이 있거나, GPU 정보가 없는 경우만 포함
            if '외장그래픽' in spec_text or 'rtx' in spec_text or 'gtx' in spec_text or 'radeon' in spec_text or 'rx' in spec_text:
                valid_products.append(p)
            elif p['score'] > 50:  # 점수가 높으면 포함 (외장 그래픽이 있을 가능성)
                valid_products.append(p)
        
        # 외장 그래픽이 있는 제품이 있으면 그것만 반환
        if valid_products:
            return valid_products[:3]
        # 없으면 점수가 높은 것 중에서 선택 (하지만 내장 그래픽만 있는 것은 제외)
        filtered_products = [p for p in scored_products if p['score'] > 0 and 
                            not ('내장그래픽' in str(p.get('상세스펙', '')).lower() and 
                                 '외장그래픽' not in str(p.get('상세스펙', '')).lower())]
        return filtered_products[:3] if filtered_products else []
    
    # 상위 3개 반환 (점수가 0 이상인 것만)
    valid_products = [p for p in scored_products if p['score'] > 0]
    return valid_products[:3] if valid_products else scored_products[:3]

def generate_response_with_gemini(
    user_input: str,
    conversation_context: str,
    spec_info: Optional[Dict] = None,
    recommended_products: Optional[List] = None,
    gemini_api_key: str = None,
    model_name: str = 'gemini-2.5-flash'
) -> str:
    """Gemini를 사용하여 응답 생성"""
    if not gemini_api_key:
        return "API 키가 설정되지 않았습니다."
    
    try:
        # 모델 초기화
        model, error = initialize_gemini_model(gemini_api_key, model_name)
        if model is None:
            return error or "모델을 초기화할 수 없습니다."
        
        prompt = f"""당신은 채널코퍼레이션의 '비즈니스 컨시어지' 정신을 구현하는 테크 전문 쇼핑 가이드 챗봇입니다.
친절하고 전문적인 톤으로 사용자에게 도움을 제공하세요.

대화 맥락:
{conversation_context}

사용자 입력: {user_input}
"""
        
        if spec_info and recommended_products:
            prompt += f"""
검색된 시스템 사양 정보:
{json.dumps(spec_info, ensure_ascii=False, indent=2)}

추천 상품:
{json.dumps(recommended_products, ensure_ascii=False, indent=2)}

위 정보를 바탕으로 전문적이고 친절한 답변을 생성해주세요.
"""
        elif recommended_products:
            # spec_info는 없지만 추천 상품이 있는 경우 (추가 대화)
            prompt += f"""
이전에 추천한 상품:
{json.dumps(recommended_products, ensure_ascii=False, indent=2)}

사용자의 추가 질문이나 요청에 대해 위 추천 상품 정보를 참고하여 친절하고 전문적으로 답변해주세요.
"""
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        error_str = str(e)
        # API 할당량 초과 오류 처리
        if '429' in error_str or 'quota' in error_str.lower() or 'exceeded' in error_str.lower():
            # 할당량 초과 시 fallback 메시지 생성
            if recommended_products and len(recommended_products) > 0:
                fallback_msg = f"""안녕하세요! 현재 API 할당량이 일시적으로 초과되어 자동 응답 생성에 제한이 있습니다.

하지만 고객님의 요구사항에 맞춰 {len(recommended_products)}개의 추천 제품을 찾았습니다. 아래 제품들을 확인해보시고, 추가 질문이 있으시면 말씀해주세요.

추천 제품:
"""
                for i, product in enumerate(recommended_products[:3], 1):
                    fallback_msg += f"\n{i}. {product.get('상품명', '')} - {format_price(product.get('최저가', ''))}"
                
                return fallback_msg
            else:
                return "죄송합니다. 현재 API 할당량이 일시적으로 초과되어 응답 생성에 제한이 있습니다. 잠시 후 다시 시도해주시거나, 다른 조건으로 검색해보시겠어요?"
        else:
            return f"응답 생성 오류: {str(e)}"

# 메인 UI (챗봇 위젯 모드)
# 타이틀과 구분선은 CSS로 숨김 처리됨

# 상품 데이터 자동 로드 (없으면 다시 시도)
if st.session_state.products_df is None:
    st.session_state.products_df = load_products_data()

# 상품 데이터 확인 (간단한 표시만, 챗봇 위젯 모드에서는 불필요한 메시지 최소화)
if st.session_state.products_df is None:
    st.warning("⚠️ 상품 데이터 파일(electronics_data.csv)을 찾을 수 없습니다.")
elif len(st.session_state.products_df) == 0:
    st.warning("⚠️ 상품 데이터가 비어있습니다.")
# 데이터가 있으면 조용히 사용 (메시지 표시 안 함)

# 타이틀
st.title("💻 테크 전문 쇼핑 가이드 챗봇")

# API 키 확인
if not st.session_state.gemini_api_key or not st.session_state.tavily_api_key:
    st.error("⚠️ API 키가 설정되지 않았습니다.")
else:
    # 초기 환영 메시지 (채팅 히스토리가 비어있을 때)
    if len(st.session_state.chat_history) == 0:
        welcome_msg = "안녕하세요! 💻 테크 전문 쇼핑 가이드 챗봇입니다. PC나 노트북에 대해 궁금한 점이 있으시면 언제든 말씀해주세요. 어떤 제품을 찾고 계신가요?"
        st.session_state.chat_history.append({'role': 'bot', 'content': welcome_msg})
    
    # 채팅 히스토리 표시
    for message in st.session_state.chat_history:
        if message['role'] == 'user':
            # 사용자 메시지는 말풍선 스타일로 감싸기
            st.markdown(
                f'<div class="chat-message user-message">{message["content"]}</div>',
                unsafe_allow_html=True,
            )
        elif message['role'] == 'bot':
            # 제품 추천 메시지인 경우: 이미 완전한 HTML(카드 포함)이므로 그대로 렌더링
            if message.get('type') == 'products':
                st.markdown(message["content"], unsafe_allow_html=True)
            else:
                # 일반 텍스트 메시지는 봇 말풍선 스타일로 감싸기
                st.markdown(
                    f'<div class="chat-message bot-message">{message["content"]}</div>',
                    unsafe_allow_html=True,
                )
    
    # 사용자 입력
    user_input = st.chat_input("메시지를 입력하세요...")
    
    if user_input:
        # 사용자 메시지 추가
        st.session_state.chat_history.append({'role': 'user', 'content': user_input})
        
        # 의도 감지
        if st.session_state.conversation_state == 'idle':
            intent = detect_intent(user_input)
            if intent:
                st.session_state.user_intent = intent
                st.session_state.conversation_state = 'usage_asked'
                
                bot_response = f"지금 {intent}를 찾고 계시네요! 최적의 제품을 추천해드리기 위해 용도가 무엇인지 여쭤봐도 될까요? (예: 게임용, 영상 편집용, 사무용, 인강용)"
                st.session_state.chat_history.append({'role': 'bot', 'content': bot_response})
                st.rerun()
            else:
                bot_response = "안녕하세요! PC나 노트북에 대해 궁금한 점이 있으시면 언제든 말씀해주세요. 어떤 제품을 찾고 계신가요?"
                st.session_state.chat_history.append({'role': 'bot', 'content': bot_response})
                st.rerun()
        
        # 용도 질문 단계
        elif st.session_state.conversation_state == 'usage_asked':
            usage_keywords = {
                '게임용': ['게임', '게이밍', 'gaming', '롤', '배그', '오버워치'],
                '작업용': ['작업', '편집', '영상', '프리미어', '에프터이펙트', '포토샵'],
                '사무용': ['사무', '오피스', '문서', '워드', '엑셀'],
                '인강용': ['인강', '강의', '학습', '온라인']
            }
            
            user_input_lower = user_input.lower()
            detected_usage = None
            for usage, keywords in usage_keywords.items():
                for keyword in keywords:
                    if keyword in user_input_lower:
                        detected_usage = usage
                        break
                if detected_usage:
                    break
            
            if detected_usage:
                st.session_state.user_usage = detected_usage
                st.session_state.conversation_state = 'software_asked'
                
                if detected_usage in ['게임용', '작업용']:
                    bot_response = f"{detected_usage}이시군요! 어떤 게임(또는 소프트웨어)을 주로 사용하시나요? (예: 롤, 배그, 프리미어 프로, 포토샵 등)"
                else:
                    bot_response = f"{detected_usage}이시군요! 어떤 소프트웨어나 작업을 주로 하시나요?"
                
                st.session_state.chat_history.append({'role': 'bot', 'content': bot_response})
                st.rerun()
            else:
                bot_response = "용도를 좀 더 구체적으로 알려주시면 더 정확한 추천을 드릴 수 있습니다. (게임용, 작업용, 사무용, 인강용 중 선택)"
                st.session_state.chat_history.append({'role': 'bot', 'content': bot_response})
                st.rerun()
        
        # 소프트웨어 질문 단계
        elif st.session_state.conversation_state == 'software_asked':
            st.session_state.user_software = user_input
            st.session_state.conversation_state = 'budget_asked'
            
            bot_response = "알겠습니다! 예산이 얼마 정도 되시나요? (예: 100만원, 200만원, 300만원 이상 등)"
            st.session_state.chat_history.append({'role': 'bot', 'content': bot_response})
            st.rerun()
        
        # 예산 질문 단계
        elif st.session_state.conversation_state == 'budget_asked':
            # 예산 숫자 추출
            budget_numbers = re.findall(r'(\d+)\s*만?\s*원?', user_input)
            if budget_numbers:
                st.session_state.user_budget = int(budget_numbers[0]) * 10000  # 만원 단위로 변환
            else:
                # 숫자만 추출
                numbers = re.findall(r'\d+', user_input.replace(',', ''))
                if numbers:
                    budget_value = int(numbers[0])
                    if budget_value < 1000:  # 1000 미만이면 만원 단위로 간주
                        st.session_state.user_budget = budget_value * 10000
                    else:
                        st.session_state.user_budget = budget_value
            
            if st.session_state.user_intent == '노트북':
                st.session_state.conversation_state = 'weight_asked'
                bot_response = "예산을 확인했습니다! 무게에 대한 선호도가 있으신가요? (예: 가벼운 것, 보통, 무거워도 괜찮음)"
            else:
                # 데스크탑은 무게 질문 건너뛰기
                st.session_state.user_weight_preference = '보통'  # 데스크탑은 무게 무관
                st.session_state.conversation_state = 'portable_asked'
                bot_response = "예산을 확인했습니다! 휴대용이 필요하신가요? (예: 네, 아니오)"
            
            st.session_state.chat_history.append({'role': 'bot', 'content': bot_response})
            st.rerun()
        
        # 무게 질문 단계 (노트북만)
        elif st.session_state.conversation_state == 'weight_asked':
            user_input_lower = user_input.lower()
            if any(kw in user_input_lower for kw in ['가벼운', '가볍', '경량', 'light', '1kg', '1.5kg']):
                st.session_state.user_weight_preference = '가벼운'
            elif any(kw in user_input_lower for kw in ['무거운', '무거워', 'heavy', '3kg', '2.5kg']):
                st.session_state.user_weight_preference = '무거워도됨'
            else:
                st.session_state.user_weight_preference = '보통'
            
            st.session_state.conversation_state = 'portable_asked'
            bot_response = "알겠습니다! 휴대용이 필요하신가요? (예: 네, 아니오)"
            st.session_state.chat_history.append({'role': 'bot', 'content': bot_response})
            st.rerun()
        
        # 휴대용 질문 단계
        elif st.session_state.conversation_state == 'portable_asked':
            user_input_lower = user_input.lower()
            if any(kw in user_input_lower for kw in ['네', '예', 'yes', '필요', '있어', '맞아']):
                st.session_state.user_portable_need = True
            else:
                st.session_state.user_portable_need = False
            
            # 모든 정보 수집 완료, 제품 추천 시작
            st.session_state.conversation_state = 'products_recommended'
            
            # 로딩 상태 표시
            loading_placeholder = st.empty()
            
            with loading_placeholder.container():
                st.info("🔄 **처리 중입니다. 잠시만 기다려주세요...**")
                progress_bar = st.progress(0)
                status_text = st.empty()
            
            # 1단계: 시스템 요구사항 검색
            status_text.text("📡 1/3 단계: 시스템 요구사항 검색 중...")
            progress_bar.progress(33)
            spec_info = search_system_requirements(
                st.session_state.user_software,
                st.session_state.tavily_api_key
            )
            st.session_state.spec_info = spec_info  # 세션 상태에 저장
            
            # 2단계: 상품 매칭
            status_text.text("🔍 2/3 단계: 최적의 제품을 찾는 중...")
            progress_bar.progress(66)
            recommended_products = match_products_by_spec(
                spec_info,
                st.session_state.products_df,
                st.session_state.user_intent,
                st.session_state.user_budget,
                st.session_state.user_weight_preference,
                st.session_state.user_portable_need
            )
            st.session_state.recommended_products = recommended_products
            
            # 3단계: 응답 생성
            status_text.text("✍️ 3/3 단계: 전문가 답변 생성 중...")
            progress_bar.progress(100)
            conversation_context = f"""
사용자 의도: {st.session_state.user_intent}
용도: {st.session_state.user_usage}
소프트웨어: {st.session_state.user_software}
예산: {format_price(st.session_state.user_budget) if st.session_state.user_budget else '제한 없음'}
무게 선호도: {st.session_state.user_weight_preference if st.session_state.user_weight_preference else '무관'}
휴대용 필요: {'예' if st.session_state.user_portable_need else '아니오'}
"""
            
            bot_response = generate_response_with_gemini(
                user_input,
                conversation_context,
                spec_info,
                recommended_products,
                st.session_state.gemini_api_key,
                st.session_state.get('gemini_model', 'gemini-2.5-flash')
            )
            
            # 로딩 표시 제거
            loading_placeholder.empty()
            
            # 설명과 제품 카드를 하나의 메시지로 통합
            if recommended_products and len(recommended_products) > 0:
                # 제품 설명 생성
                product_descriptions = {}
                if st.session_state.gemini_api_key:
                    desc_loading = st.empty()
                    with desc_loading.container():
                        st.info(f"📝 **상품 설명을 생성하는 중입니다... (0/{len(recommended_products)})**")
                    
                    for i, product in enumerate(recommended_products):
                        with desc_loading.container():
                            st.info(f"📝 **상품 설명을 생성하는 중입니다... ({i+1}/{len(recommended_products)})**")
                            try:
                                model, error = initialize_gemini_model(
                                    st.session_state.gemini_api_key,
                                    st.session_state.get('gemini_model', 'gemini-2.5-flash')
                                )
                                if model:
                                    description_prompt = f"""다음 제품에 대해 2-3문장으로 간략하고 전문적인 설명을 작성해주세요.
사용자 요구사항:
- 용도: {st.session_state.user_usage}
- 소프트웨어: {st.session_state.user_software}
- 예산: {format_price(st.session_state.user_budget) if st.session_state.user_budget else '제한 없음'}
- 제품 타입: {st.session_state.user_intent}

제품 정보:
- 상품명: {product.get('상품명', '')}
- 가격: {format_price(product.get('최저가', ''))}
- 스펙: {str(product.get('상세스펙', ''))[:300]}

이 제품이 사용자 요구사항에 왜 적합한지, 주요 특징과 장점을 간략히 설명해주세요. 친절하고 전문적인 톤으로 작성해주세요."""
                                    
                                    response = model.generate_content(description_prompt)
                                    product_descriptions[i] = response.text.strip()
                                else:
                                    product_descriptions[i] = None
                            except Exception as e:
                                error_str = str(e)
                                if '429' in error_str or 'quota' in error_str.lower() or 'exceeded' in error_str.lower():
                                    with desc_loading.container():
                                        st.warning("⚠️ API 할당량이 초과되어 상품 설명 생성을 중단했습니다. 제품 정보는 정상적으로 표시됩니다.")
                                    break
                                product_descriptions[i] = None
                    
                    desc_loading.empty()
                
                # 제품 카드 HTML 생성
                products_html = generate_products_html(
                    recommended_products,
                    product_descriptions,
                    st.session_state.user_software,
                    st.session_state.user_usage
                )
                
                # 설명과 제품 카드를 하나의 HTML 메시지로 통합
                # bot_response를 HTML로 이스케이프하여 안전하게 포함
                bot_response_escaped = escape_html(bot_response)
                combined_content = f'<div class="bot-response-text">{bot_response_escaped}</div>{products_html}'
                st.session_state.chat_history.append({
                    'role': 'bot',
                    'type': 'products',
                    'content': combined_content,
                    'products': recommended_products
                })
            else:
                # 제품이 없으면 설명만 추가
                st.session_state.chat_history.append({'role': 'bot', 'content': bot_response})
            
            st.rerun()
        
        # 제품 추천 후 추가 질문/대화 처리
        elif st.session_state.conversation_state == 'products_recommended':
            # 사용자 입력에서 조건 변경 감지
            needs_recommendation = False
            old_budget = st.session_state.user_budget
            old_weight = st.session_state.user_weight_preference
            old_portable = st.session_state.user_portable_need
            
            # 명시적 재추천 요청 감지
            user_input_lower = user_input.lower()
            if any(kw in user_input_lower for kw in ['다시', '재추천', '다시 찾아', '다시 추천', '다시 찾아봐', '다시 보여줘', '다시 보여', '다시 검색']):
                needs_recommendation = True
            
            # 예산 변경 감지
            budget_numbers = re.findall(r'(\d+)\s*만?\s*원?', user_input)
            if budget_numbers:
                new_budget = int(budget_numbers[0]) * 10000
                if new_budget != old_budget:
                    st.session_state.user_budget = new_budget
                    needs_recommendation = True
            else:
                # 숫자만 추출
                numbers = re.findall(r'\d+', user_input.replace(',', ''))
                if numbers:
                    budget_value = int(numbers[0])
                    if budget_value < 1000:
                        new_budget = budget_value * 10000
                    else:
                        new_budget = budget_value
                    if new_budget != old_budget and new_budget > 100000:  # 10만원 이상일 때만
                        st.session_state.user_budget = new_budget
                        needs_recommendation = True
            
            # 무게 선호도 변경 감지
            if any(kw in user_input_lower for kw in ['가벼운', '가볍', '경량', 'light', '1kg', '1.5kg']):
                if st.session_state.user_weight_preference != '가벼운':
                    st.session_state.user_weight_preference = '가벼운'
                    needs_recommendation = True
            elif any(kw in user_input_lower for kw in ['무거운', '무거워', 'heavy', '3kg', '2.5kg']):
                if st.session_state.user_weight_preference != '무거워도됨':
                    st.session_state.user_weight_preference = '무거워도됨'
                    needs_recommendation = True
            
            # 휴대용 필요 여부 변경 감지
            if any(kw in user_input_lower for kw in ['휴대', '휴대용', '포기', '안필요', '불필요']):
                if '포기' in user_input_lower or '안필요' in user_input_lower or '불필요' in user_input_lower:
                    if st.session_state.user_portable_need != False:
                        st.session_state.user_portable_need = False
                        needs_recommendation = True
                elif '필요' in user_input_lower or '있어' in user_input_lower:
                    if st.session_state.user_portable_need != True:
                        st.session_state.user_portable_need = True
                        needs_recommendation = True
            
            # 조건이 변경되었으면 제품을 다시 추천
            if needs_recommendation:
                # 로딩 표시 (매번 새로 생성)
                loading_placeholder = st.empty()
                
                with loading_placeholder.container():
                    st.info("🔄 **조건이 변경되어 제품을 다시 찾는 중입니다. 잠시만 기다려주세요...**")
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                
                try:
                    # 시스템 요구사항은 이미 있으므로 재사용
                    status_text.text("🔍 최적의 제품을 다시 찾는 중...")
                    progress_bar.progress(50)
                    
                    # 저장된 spec_info 재사용
                    spec_info = st.session_state.spec_info if st.session_state.spec_info else {}
                    
                    recommended_products = match_products_by_spec(
                        spec_info,
                        st.session_state.products_df,
                        st.session_state.user_intent,
                        st.session_state.user_budget,
                        st.session_state.user_weight_preference,
                        st.session_state.user_portable_need
                    )
                    st.session_state.recommended_products = recommended_products
                    
                    status_text.text("✍️ 전문가 답변 생성 중...")
                    progress_bar.progress(100)
                    
                    conversation_context = f"""
사용자 의도: {st.session_state.user_intent}
용도: {st.session_state.user_usage}
소프트웨어: {st.session_state.user_software}
예산: {format_price(st.session_state.user_budget) if st.session_state.user_budget else '제한 없음'} (변경됨)
무게 선호도: {st.session_state.user_weight_preference if st.session_state.user_weight_preference else '무관'}
휴대용 필요: {'예' if st.session_state.user_portable_need else '아니오'}

사용자가 조건을 변경하여 새로운 제품 추천을 요청했습니다.
"""
                    
                    # 제품이 있는지 확인
                    if recommended_products and len(recommended_products) > 0:
                        bot_response = generate_response_with_gemini(
                            user_input,
                            conversation_context,
                            spec_info,
                            recommended_products,
                            st.session_state.gemini_api_key,
                            st.session_state.get('gemini_model', 'gemini-2.5-flash')
                        )
                        
                        # 기존 제품 메시지 제거
                        st.session_state.chat_history = [msg for msg in st.session_state.chat_history if msg.get('type') != 'products']
                        
                        # 제품 카드 HTML 생성 (재추천용 - 간단한 설명만)
                        products_html = generate_products_html(
                            recommended_products,
                            None,  # 재추천 시에는 설명 생성 안 함 (빠른 응답)
                            st.session_state.user_software,
                            st.session_state.user_usage
                        )
                        
                        # 설명과 제품 카드를 하나의 HTML 메시지로 통합
                        bot_response_escaped = escape_html(bot_response)
                        combined_content = f'<div class="bot-response-text">{bot_response_escaped}</div>{products_html}'
                        st.session_state.chat_history.append({
                            'role': 'bot',
                            'type': 'products',
                            'content': combined_content,
                            'products': recommended_products
                        })
                    else:
                        # 제품을 찾지 못한 경우
                        bot_response = f"""죄송합니다. 변경된 조건(예산: {format_price(st.session_state.user_budget) if st.session_state.user_budget else '제한 없음'}, 무게: {st.session_state.user_weight_preference if st.session_state.user_weight_preference else '무관'}, 휴대용: {'예' if st.session_state.user_portable_need else '아니오'})에 맞는 제품을 찾지 못했습니다. 

다음과 같은 방법을 시도해보시겠어요?
1. 예산을 조금 더 상향 조정
2. 무게나 휴대성 조건을 완화
3. 다른 제품 타입 고려

원하시는 방향을 알려주시면 다시 찾아드리겠습니다."""
                        st.session_state.chat_history.append({'role': 'bot', 'content': bot_response})
                    
                    # 로딩 표시 제거 (응답 생성 후)
                    loading_placeholder.empty()
                    
                    # 제품이 있으면 바로 표시되도록 rerun
                    st.rerun()
                    
                except Exception as e:
                    # 오류 발생 시 로딩 표시 제거
                    loading_placeholder.empty()
                    error_str = str(e)
                    if '429' in error_str or 'quota' in error_str.lower() or 'exceeded' in error_str.lower():
                        error_msg = """⚠️ **API 할당량 초과 안내**

현재 Google Gemini API의 무료 티어 할당량(하루 20회)을 초과했습니다. 

**해결 방법:**
1. 잠시 후(약 30초~1분) 다시 시도해주세요
2. Google AI Studio에서 유료 플랜으로 업그레이드하세요
3. 다른 Gemini 모델을 사용하세요 (gemini-1.5-pro 등)

추천 제품은 아래에 표시되어 있으니 확인해보시고, 추가 질문이 있으시면 나중에 다시 시도해주세요."""
                    else:
                        error_msg = f"오류가 발생했습니다: {str(e)}"
                    st.session_state.chat_history.append({'role': 'bot', 'content': error_msg})
                    st.rerun()
            
            # 조건 변경이 없으면 일반 대화 처리
            else:
                # 로딩 표시 (매번 새로 생성)
                loading_placeholder = st.empty()
                
                try:
                    with loading_placeholder.container():
                        st.info("💬 **답변을 생성하는 중입니다. 잠시만 기다려주세요...**")
                    
                    conversation_context = f"""
사용자 의도: {st.session_state.user_intent}
용도: {st.session_state.user_usage}
소프트웨어: {st.session_state.user_software}
예산: {format_price(st.session_state.user_budget) if st.session_state.user_budget else '제한 없음'}
무게 선호도: {st.session_state.user_weight_preference if st.session_state.user_weight_preference else '무관'}
휴대용 필요: {'예' if st.session_state.user_portable_need else '아니오'}

이전 대화 내용:
{json.dumps([msg for msg in st.session_state.chat_history[-10:]], ensure_ascii=False, indent=2)}

추천된 상품:
{json.dumps(st.session_state.recommended_products, ensure_ascii=False, indent=2)}
"""
                    
                    # Gemini로 응답 생성
                    bot_response = generate_response_with_gemini(
                        user_input,
                        conversation_context,
                        None,  # spec_info는 이미 추천에 사용됨
                        st.session_state.recommended_products,
                        st.session_state.gemini_api_key,
                        st.session_state.get('gemini_model', 'gemini-2.5-flash')
                    )
                    
                    # 로딩 표시 제거 (응답 생성 후)
                    loading_placeholder.empty()
                    
                    st.session_state.chat_history.append({'role': 'bot', 'content': bot_response})
                    st.rerun()
                    
                except Exception as e:
                    # 오류 발생 시 로딩 표시 제거
                    loading_placeholder.empty()
                    error_str = str(e)
                    if '429' in error_str or 'quota' in error_str.lower() or 'exceeded' in error_str.lower():
                        error_msg = """⚠️ **API 할당량 초과 안내**

현재 Google Gemini API의 무료 티어 할당량(하루 20회)을 초과했습니다. 

**해결 방법:**
1. 잠시 후(약 30초~1분) 다시 시도해주세요
2. Google AI Studio에서 유료 플랜으로 업그레이드하세요
3. 다른 Gemini 모델을 사용하세요 (gemini-1.5-pro 등)

추천 제품은 아래에 표시되어 있으니 확인해보시고, 추가 질문이 있으시면 나중에 다시 시도해주세요."""
                    else:
                        error_msg = f"오류가 발생했습니다: {str(e)}"
                    st.session_state.chat_history.append({'role': 'bot', 'content': error_msg})
                    st.rerun()
        
        # 추천 상품을 채팅 히스토리에 추가 (한 번만)
        if (st.session_state.conversation_state == 'products_recommended' and 
            st.session_state.recommended_products and 
            len(st.session_state.recommended_products) > 0 and
            not any(msg.get('type') == 'products' for msg in st.session_state.chat_history)):
            
            # 각 상품에 대한 설명 생성
            product_descriptions = {}
            if st.session_state.gemini_api_key and len(st.session_state.recommended_products) > 0:
                desc_loading = st.empty()
                with desc_loading.container():
                    st.info(f"📝 **상품 설명을 생성하는 중입니다... (0/{len(st.session_state.recommended_products)})**")
                
                for i, product in enumerate(st.session_state.recommended_products):
                    with desc_loading.container():
                        st.info(f"📝 **상품 설명을 생성하는 중입니다... ({i+1}/{len(st.session_state.recommended_products)})**")
                        try:
                            model, error = initialize_gemini_model(
                                st.session_state.gemini_api_key,
                                st.session_state.get('gemini_model', 'gemini-2.5-flash')
                            )
                            if model:
                                description_prompt = f"""다음 제품에 대해 2-3문장으로 간략하고 전문적인 설명을 작성해주세요.
사용자 요구사항:
- 용도: {st.session_state.user_usage}
- 소프트웨어: {st.session_state.user_software}
- 예산: {format_price(st.session_state.user_budget) if st.session_state.user_budget else '제한 없음'}
- 제품 타입: {st.session_state.user_intent}

제품 정보:
- 상품명: {product.get('상품명', '')}
- 가격: {format_price(product.get('최저가', ''))}
- 스펙: {str(product.get('상세스펙', ''))[:300]}

이 제품이 사용자 요구사항에 왜 적합한지, 주요 특징과 장점을 간략히 설명해주세요. 친절하고 전문적인 톤으로 작성해주세요."""
                                
                                response = model.generate_content(description_prompt)
                                product_descriptions[i] = response.text.strip()
                            else:
                                product_descriptions[i] = None
                        except Exception as e:
                            error_str = str(e)
                            # API 할당량 초과 시 설명 생성 건너뛰기
                            if '429' in error_str or 'quota' in error_str.lower() or 'exceeded' in error_str.lower():
                                # 할당량 초과 시 나머지 설명 생성 중단
                                with desc_loading.container():
                                    st.warning("⚠️ API 할당량이 초과되어 상품 설명 생성을 중단했습니다. 제품 정보는 정상적으로 표시됩니다.")
                                break
                            product_descriptions[i] = None
                
                # 설명 생성 완료 후 로딩 표시 제거
                desc_loading.empty()
            
            # 제품 카드 HTML 생성
            products_html = generate_products_html(
                st.session_state.recommended_products,
                product_descriptions,
                st.session_state.user_software,
                st.session_state.user_usage
            )
            
            # 채팅 히스토리에 제품 추천 메시지 추가
            st.session_state.chat_history.append({
                'role': 'bot',
                'type': 'products',
                'content': products_html,
                'products': st.session_state.recommended_products
            })
            st.rerun()
        
        # 대화 초기화 버튼 (채팅 히스토리 아래에 표시)
        if st.session_state.conversation_state == 'products_recommended' and len(st.session_state.chat_history) > 0:
            st.markdown("---")
            if st.button("🔄 새로운 상담 시작"):
                st.session_state.conversation_state = 'idle'
                st.session_state.user_intent = None
                st.session_state.user_usage = None
                st.session_state.user_software = None
                st.session_state.user_budget = None
                st.session_state.user_weight_preference = None
                st.session_state.user_portable_need = None
                st.session_state.recommended_products = []
                st.session_state.spec_info = None
                st.session_state.chat_history = []
                st.rerun()