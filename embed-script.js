/**
 * 채널톡 스타일 챗봇 위젯 임베드 스크립트
 * 웹사이트에 이 스크립트를 추가하면 챗봇이 자동으로 로드됩니다.
 * 
 * 사용법:
 * <script src="https://your-domain.com/embed-script.js" data-streamlit-url="http://localhost:8501"></script>
 */

(function() {
    'use strict';

    // 설정
    const config = {
        streamlitUrl: document.currentScript?.getAttribute('data-streamlit-url') || 'http://localhost:8501',
        buttonColor: document.currentScript?.getAttribute('data-button-color') || '#6336FF',
        position: document.currentScript?.getAttribute('data-position') || 'bottom-right' // bottom-right, bottom-left
    };

    // 스타일 생성
    const style = document.createElement('style');
    style.textContent = `
        #channel-chatbot-widget {
            position: fixed;
            ${config.position === 'bottom-left' ? 'left: 20px;' : 'right: 20px;'}
            bottom: 20px;
            z-index: 9999;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
        }

        #chatbot-button {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background-color: ${config.buttonColor};
            color: white;
            border: none;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(99, 54, 255, 0.4);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            transition: all 0.3s ease;
        }

        #chatbot-button:hover {
            background-color: ${config.buttonColor}dd;
            transform: scale(1.1);
            box-shadow: 0 6px 16px rgba(99, 54, 255, 0.5);
        }

        #chatbot-window {
            position: absolute;
            bottom: 80px;
            ${config.position === 'bottom-left' ? 'left: 0;' : 'right: 0;'}
            width: 400px;
            height: 600px;
            background-color: white;
            border-radius: 16px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
            display: none;
            flex-direction: column;
            overflow: hidden;
        }

        #chatbot-window.open {
            display: flex;
        }

        #chatbot-header {
            background-color: ${config.buttonColor};
            color: white;
            padding: 16px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        #chatbot-header h3 {
            margin: 0;
            font-size: 18px;
            font-weight: 600;
        }

        #chatbot-close {
            background: none;
            border: none;
            color: white;
            font-size: 24px;
            cursor: pointer;
            padding: 0;
            width: 30px;
            height: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        #chatbot-close:hover {
            opacity: 0.7;
        }

        #chatbot-iframe {
            flex: 1;
            border: none;
            width: 100%;
            height: 100%;
        }

        @media (max-width: 768px) {
            #chatbot-window {
                width: 100vw;
                height: 100vh;
                bottom: 0;
                ${config.position === 'bottom-left' ? 'left: 0;' : 'right: 0;'}
                border-radius: 0;
            }

            #channel-chatbot-widget {
                ${config.position === 'bottom-left' ? 'left: 10px;' : 'right: 10px;'}
                bottom: 10px;
            }
        }
    `;
    document.head.appendChild(style);

    // HTML 생성
    const widget = document.createElement('div');
    widget.id = 'channel-chatbot-widget';
    widget.innerHTML = `
        <div id="chatbot-window">
            <div id="chatbot-header">
                <h3>💻 테크 전문 쇼핑 가이드</h3>
                <button id="chatbot-close">×</button>
            </div>
            <iframe 
                id="chatbot-iframe"
                src="${config.streamlitUrl}"
                title="테크 전문 쇼핑 가이드 챗봇"
            ></iframe>
        </div>
        <button id="chatbot-button" aria-label="챗봇 열기">💬</button>
    `;
    document.body.appendChild(widget);

    // 이벤트 리스너
    const chatbotButton = document.getElementById('chatbot-button');
    const chatbotWindow = document.getElementById('chatbot-window');
    const chatbotClose = document.getElementById('chatbot-close');

    chatbotButton.addEventListener('click', function() {
        chatbotWindow.classList.toggle('open');
        chatbotButton.textContent = chatbotWindow.classList.contains('open') ? '✕' : '💬';
    });

    chatbotClose.addEventListener('click', function() {
        chatbotWindow.classList.remove('open');
        chatbotButton.textContent = '💬';
    });
})();