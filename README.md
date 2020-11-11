# Chatbot for subway system
Navigation system for subway system (Line 1-9, AREX, Kyeongui-Jungang Line, Bundang Line, Ui-Shinseol Line, etc (Seoul, Incheon, Gyeonggi Area) and information about toilets inside the ticket barrier.
Used Natural Language Processing (NLP) for Korean by MeCab, ODSay API for metro information, and used --- algorithm for shortest path and shortest time route.
First deployed on heroku for testing, then used AWS EC2.

https://youtu.be/t0etGpdZcx0

### SW
- Windows, Linux for development settings
- git, putty, cyberduck for management and server communiation
- AWS EC2 for server, AWS RDS for database, AWS S3 for image datas
- Python 3.7.5 Flask (backend) + ODsay API + LINE (frontend)

### 개발 배경
생활에 필요한 정보를 사용자에게 전달할 때, 단순 검색 결과 화면보다 챗봇을 사용하면 더 좋을 것 같은 주제를 생각하다가 공공 시설 중에서 지하철 개찰구 안에 있는 화장실 여부를 알려 주는 챗봇을 개발하는 것으로 구체화되었다. 음성 비서나 단순 검색으로는 명쾌한 결과를 찾기 어렵고 사람들이 필요로 하지만 별도로 개발된 서비스가 없으며, 해당 서비스를 제공하는 지하철 길찾기 애플리케이션 또한 별도로 설치해야 하며 사용이 불편하다. 친구 추가만을 통해 서비스를 제공할 수 있으므로 접근 용이성이 큰 띵톡은 많은 사용자에게 편의를 제공할 수 있을 것이다.


### 프로젝트 소개
띵톡은 차세대 인터페이스로 각광받고 있는 챗봇과 그에 기반하는 기술인 자연어 처리 (NLP)에 대한 학습 이후 개발한 챗봇이다. 챗봇은 기존의 메신저 플랫폼 기반으로, 자동적인 화자 대 화자를 목표로 다양한 채팅 언어를 학습하여 정확히 인식하고 이를 기반으로 챗봇이 적합한 액션 (대화 및 추가적인 기능 실현)을 수행한다. 챗봇의 핵심 기능은 화자가 언급한 대화를 정확하게 인식하고, 이에 적합한 판단을 수행해야 한다. 메신저 앱인 '라인' 기반으로 작동하는 '띵톡'은 지하철 개찰구 내에 화장실이 있는 역 정보를 알려 주는 챗봇이다. 사용자는 챗봇을 이용하여 본인이 이동 중인 경로에 있는 역이나 원하는 특정 역의 화장실 정보를 알 수 있다. 방식은 크게 경로 내, 특정 역, 최단 거리, 최소 환승으로 총 4 가지가 있다.
※ 개찰구 내 화장실은 지하철 이용을 위한 요금 계산을 하는 삼발이를 지나야 갈 수 있는 화장실을 의미한다.


### 프로젝트 주요 기능
1. 사용자가 원하는 정보 인식
(활용 기술: 자연어 학습, 기계 학습 알고리즘 및 통계 분석 기법을 활용한 NLP)
2. 사용자가 원하는 정보 제공
(활용 기술: 데이터 수집 라이브러리를 이용한 파이썬 크롤링으로 정보 수집)
3. 사용자가 원하는 정보를 제공하기 위한 처리
(활용 기술: Python Flask로 서버 개발, AWS RDS와 MySQL로 데이터베이스 구축)


## Repository
### /DB
- db_creaty.py : 데이터베이스 생성
- get_station_code_at_odsay.py : 오디세이가 사용하는 역 코드 받아 오기
- info_intoilet.py : 노선별 개찰구 내 화장실이 있는 역 이름 사전
- subwayinfo.csv : 지하철 역 정보
- subway_name.json : 수도권 지하철의 모든 역 딕셔너리

### /flask_EC2
- db_connection.py : RDS와 연결하는 지점 설정
- functions.py : EC2 서버에서 사용하는 함수
- main.py : EC2 서버 메인 함수 (backend)
- replace_correct_word.py : 사용자의 오타 입력에 대해 처리하는 함수를 사용한 처리 작업 수행
- typing_error_processing.py : 사용자의 오타 입력에 대해 처리하는 함수
- stage_control.py : 단계 제어 함수

### /flask_heroku
- Procfile : 배포 방식
- main.py : heroku 서버 메인 함수 (frontend)
- requirements.txt : 환경 명시
- runtime.txt : 버전 명시

## Scenarios
1. 경로 내: 사용자 경로 입력 -> 경로 확인 -> 정보 제공
2. 특정 역: 사용자 역명 입력 -> 역명 확인 -> 정보 제공
3. 최단 경로: 사용자 경로 입력 -> 정보 확인 -> 정보 제공
4. 최소 환승: 사용자 경로 입력 -> 정보 확인 -> 정보 제공
5. 종료

## Output
### 1. 특정 키워드 확인
flask_EC2/main.py

특정 키워드 입력하였는지 검사를 수행 후 stage 처리한다. 특정 키워드가 사용자가 입력한 텍스트에 있을 경우, 해당하는 stage에 진입하도록 처리한다. 입력 이벤트가 발생하였을 시, Konlpy의 Mecab Tag 형태소 분석기를 이용하여 텍스트 전체를 분석한 결과를 토대로 명사 중에 특정 키워드가 있는지 확인한다. 이를 토대로 stage 진입 또는 초기화하도록 한다. 이후에 특정 키워드가 없는 텍스트일 경우에는 기존의 사용자가 거친 stage대로 처리하도록 시나리오를 전개한다.

### 2. 한 문장 내 출발지와 도착지 확인
flask_EC2/main.py
띵톡 호출 후 "경로 내", "최단 경로", "최소 환승" 입력한 경우 수행한다. 한 문장 내에 출발지와 도착지에 해당하는 역을 확인하는 stage에 대한 처리이다. 현재 사용자의 위치와 가고자 하는 목적지를 텍스트 내에서 처리한다. 동사의 유무로 만약에 텍스트 내에 있다면, 두 개의 명사를 파악하도록 하여 처음에 등장하는 명사를 출발지, 나중에 등장하는 명사를 도착지로 설정한다. 이때 각 명사들을 DB에 존재하는 역 이름과 일치하는지 확인한다. 일치하지 않는다면 비슷한 이름들의 리스트를 후보로 제시하여 어떤 역인지 한 번 더 입력하도록 하는 stage로 접근한다. 역 정보가 모두 알맞게 입력되었다면 다음 stage로 접근한다. (현재는 동사의 유무로 텍스트 내에 2개의 역 정보가 있다고 가정하였으나 추후 변경 가능)

### 3. 특정 역 개찰구 내 화장실 유무
flask_EC2/main.py
띵톡 호출 후 특정 역 하나만을 입력한 경우 수행한다. 입력된 역에 대하여 개찰구 내 화장실 유무 정보를 확인하기 위한 stage이다. 텍스트 안에 특정 역이 있으면 개찰구 내 화장실 여부를 메시지로 출력한다. 이전 프로그램과 유사하게 일치하는 역 이름이 있는지 확인하고, 없을 시에는 후보 리스트를 제시하여 한 번 더 입력하도록 한다. 일치하는 역 이름이 있다면 해당 역에 대하여 DB에 조회하여 개찰구 내의 화장실 여부를 메시지로 출력한다.

### 4. 사용자 입력 오타 확인
flask_EC2/replace_correct_word.py
- def find_most_similiar_in_group(word, search_words), def correct_subway_word(word)
출발 역 또는 도착 역이라고 간주되는 명사 (word) 와 DB에 존재하는 역 이름들과 비교하여 검사하고, 다르다면 유사한 역 이름들을 반환한다. 인자로 받은 명사의 첫 단어가 동일한 역 이름들 중에 거리를 개산하여 가장 거리가 짧은 순서대로 최대 3개를 반환한다. 만약 첫 단어부터 동일한 역 이름이 없을 경우, 초성과 똑같은 모든 역 이름 중에서 가장 거리가 가까운 역 이름을 확인하도록 한다. Levenshtein distance를 이용하여 각 단어들을 초성, 중성, 종성으로 구분하여 유사한 정도를 계산하도록 한다.

- def compose(chosung, jungsung, jongsung), def _is_character_Korean(char), def decompose(char), def _to_base(c), def get_jamo_cost(c1, c2)
입력받은 한글을 숫자 값으로 변환 및 계산하여 초성, 중성, 종성으로 나눈다. 다음 Levenshtein distance를 이용하여 각 초성, 중성, 종성별로 철자가 다르다면 1/3씩 거리를 증가시키고, 같은 위치에 있는 글자가 아예 다르다면 1씩 거리를 증가시킨다. 비슷한 방식으로 단어 자릿수가 많거나 작을수록 1씩 거리가 증가하는 가중치로 계산하여, 유사한 단어일수록 거리가 짧아진다.

### 5. Odsay API 서비스 연동
flask_EC2/functions.py
- def get_odsay_API(lang=0, CID, SID, EID, Sopt)
출발 역과 도착 역이 파악되면 URI API 형식으로 Odsay에서 제공하는 서비스를 이용하여 지하철 내 경로를 검색한다. 출발 및 도착 역을 DB에 조회하여 Odsay에서 호환되는 지하철 역 코드를 인자로 전달받아, 이를 API 호출 형식으로 지하철 내 경로 검색 결과를 반환한다. 한국어로 결과 언어를 설정하고, 수도권 지하철 내 검색으로만 기본적으로 설정한다. 만약 "최단 경로" 방식으로 사용자가 검색한다면 Sopt 인자를 1, "최소 환승" 방식이라면 Sopt 인자를 2로 설정한다. SID와 EID는 각각 출발역, 도착역이다. API에 대한 인자 설정 완료 후 UTF-8로 encoding하여 GET 방식으로 호출하고, Odsay Server에서 얻은 json 파일을 반환한다.

### 6. Line Server와 통신
flask_heroku/main.py
- def handle_stage(event)
Line Server와 통신하여 사용자와 EC2와의 연결을 이어 주는 API 서버이다. Line Server와 EC2에서 처리하는 모든 stage 또는 특정 키워드에 대한 반응을 처리한다. Line Developer에서 callback 함수를 설정하여 address와 key를 설정하도록 하여 API 서버를 Heroku에 deploy하고, 이로 사용자가 메시지를 보내는 event 발생 시에 항상 서버에 전송한다. json 형식으로 event에 대한 내용이 담겨 있으므로 필요한 데이터만 추출하여 EC2에 POST 방식으로 데이터를 전송하고, 그로부터 얻은 결과에 따라 사용자에게 버튼 형식이나 카드 형식 등 line-bot-sdk 라이브러리에서 제공하는 UI방식으로 적절히 결과로 보낸다.
line_bot_api의 라이브러리를 활용하여 각 함수의 폼에 맞게 결과물을 출력한다. 사용자의 편의를 위하여 오타가 발생했던 단어가 있다면 후보 단어들을 선택할 수 있도록 버튼 형식으로 출력하고, 경로 내의 개찰구 안 화장실에 대한 세부 정보 및 노선 이미지 시각화를 하거나, Flex Message라는 json 형식을 커스텀으로 제작하여 경로 검색 결과를 시각화하여 출력한다.


