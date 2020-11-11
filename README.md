# Chatbot for subway system

https://youtu.be/t0etGpdZcx0

### SW
- Windows, Linux for development settings
- git, putty, cyberduck for management and server communiation
- Python 3.7.5 Django (backend) + ODsay API + LINE (frontend)

Navigation system for subway system (Line 1-9, AREX, Kyeongui-Jungang Line, Bundang Line, Ui-Shinseol Line, etc (Seoul, Incheon, Gyeonggi Area) and information about toilets inside the ticket barrier.

Used Natural Language Processing (NLP) for Korean by MeCab, ODSay API for metro information, and used --- algorithm for shortest path and shortest time route.

First deployed on heroku for testing, then used AWS EC2.


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
(활용 기술: Python Flask로 서버 개발, AWS EC2와 MySQL로 데이터베이스 구축)


##




## Scenarios
1. 경로 내: 사용자 경로 입력 -> 경로 확인 -> 정보 제공
2. 특정 역: 사용자 역명 입력 -> 역명 확인 -> 정보 제공
3. 최단 경로: 사용자 경로 입력 -> 정보 확인 -> 정보 제공
4. 최소 환승: 사용자 경로 입력 -> 정보 확인 -> 정보 제공
5. 종료










