# Nginx deployment: "$ sudo /etc/init.d/nginx start"
import requests
from flask import Flask, jsonify, request
from flask_EC2.functions import *
from flask_EC2.stage_control import *
from flask_EC2.replace_correct_word import *

app = Flask(__name__)

@app.route('/', methods=['POST'])
def manage_flow():
    # json 불러오기
    req = request.get_json()
    uid, txt, username = req['user_id'], req['message'], req['username']

    start_point = replace_num_eng_to_korean(get_start_point(uid))
    end_point = replace_num_eng_to_korean(get_end_point(uid))
    
    reply = ""
    candidate_words = []
    toilet_here = []
    route_result = []
    toilet_loc = {}
    total_time = ""
    exchange_list = []

    # stage 확인, 없을 경우 DB INSERT
    stage = check_user(uid)
    last_stage = get_last(uid)

    # txt 분기 시작 ==================================================
    # Keyword 역할 (우선순위 1위)
    # [0] 띵톡 호출 
    if "띵톡" in txt:
        # stage 초기화
        stage = initialize(uid)

    # [1] 경로내 처리
    elif "경로 내" in txt:
        # stage 조정
        stage = set_stage(uid, 1)
        # last point 저장
        set_last(uid, stage)
        # 안내 메시지
        reply = "{}님의 현재 위치와 도착지를 알려주세요. 예를 들어, A역에서 B역으로 가는 길이야! 라고 말해주세요.".format(username)

    # [10] 특정역 처리
    elif "특정역" in txt: 
        reply = "'A역'과 같이 역 이름을 말씀해주세요! 개찰구 안에 화장실이 있는지 알려드릴게요."
        stage = set_stage(uid, 10)
    # [21] 최단시간 경로 찾기
    elif txt == "최단 경로":
        # stage 조정
        stage = set_stage(uid, 21)
        # last point 저장
        set_last(uid, stage)
        reply = "{}님의 현재 위치와 도착지를 알려주세요. 예를 들어, A역에서 B역으로 가는 길이야! 라고 말해주세요.".format(username)
    # [22] 최소환승 경로 찾기
    elif txt == "최소 환승":
        # stage 조정
        stage = set_stage(uid, 22)
        # last point 저장
        set_last(uid, stage)
        reply = "{}님의 현재 위치와 도착지를 알려주세요. 예를 들어, A역에서 B역으로 가는 길이야! 라고 말해주세요.".format(username)

    # [24] 종료
    elif "종료" in txt:
        # stage 초기화
        stage = set_stage(uid, 24)
        # 메시지 
        reply = "또 필요한 일이 생기면 이름을 불러주세요~ 안녕!"
    # txt 분기 종료 ==========================================================
    
    # 해당하는 keyword가 아닐 경우, stage 분기로 나눠서 각 시나리오 진행
    # stage 별 분기 시작 =====================================================
    else:
    
        # ===========================================================================
        # 띵톡 호출 후, "경로 내", "최단 경로", "최소 환승" 입력한 경우 첫 입력 =========
        if stage in [1, 5, 21, 22]:
            
            # 문장 내에 동사가 있는 경우.
            if is_vv(txt):
                stage = set_stage(uid, 2)

                start_point, end_point = extract_start_end(txt)
                start_check_is_correct = correct_subway_word(start_point)
                end_check_is_correct = correct_subway_word(end_point)

                if len(start_check_is_correct) == 1 and len(end_check_is_correct) == 1:
                    stage = set_stage(uid, 4)
                    start_point = set_start_point(uid, get_official_name(start_check_is_correct[0][0]))
                    end_point = set_end_point(uid, get_official_name(end_check_is_correct[0][0]))

                elif len(start_check_is_correct) > 1 and len(end_check_is_correct) == 1:
                    stage = set_stage(uid, 33)
                    end_point = set_end_point(uid, get_official_name(end_check_is_correct[0][0]))
                    reply = "도착지 역은 {} 이군요! 근데 출발역은 어디이신가요? 아래의 보기에서 알려주세요!".format(end_point)
                    candidate_words = [get_official_name(word[0]) for word in start_check_is_correct]
                
                elif len(start_check_is_correct) == 1 and len(end_check_is_correct) > 1:
                    stage = set_stage(uid, 34)
                    start_point = set_start_point(uid, get_official_name(start_check_is_correct[0][0]))
                    reply = "출발지 역은 {} 이군요! 근데 도착역은 어디이신가요? 아래의 보기에서 알려주세요!".format(start_point)
                    candidate_words = [get_official_name(word[0]) for word in end_check_is_correct]

                else:
                    stage = set_stage(uid, 3)
                    reply = "역 이름을 잘 모르겠어요 T.T 출발지 역부터 다시 말해주세요!"
                    candidate_words = [get_official_name(word[0]) for word in start_check_is_correct]
                    set_end_point(uid, end_point) # 오타난 단어 일단 DB에 저장

            # 문장 내에 동사 또는 부사격조사가 없는 경우. 
            else:
                stage = set_stage(uid, 2)

                start_point, end_point = alter_extract_start_end(txt) 
                start_check_is_correct = correct_subway_word(start_point)
                end_check_is_correct = correct_subway_word(end_point)

                if len(start_check_is_correct) == 1 and len(end_check_is_correct) == 1:
                    stage = set_stage(uid, 4)
                    start_point = set_start_point(uid, get_official_name(start_check_is_correct[0][0]))
                    end_point = set_end_point(uid, get_official_name(end_check_is_correct[0][0]))

                elif len(start_check_is_correct) > 1 and len(end_check_is_correct) == 1:
                    stage = set_stage(uid, 33)
                    end_point = set_end_point(uid, get_official_name(end_check_is_correct[0][0]))
                    reply = "도착지 역은 {} 이군요! 근데 출발역은 어디이신가요? 아래의 보기에서 알려주세요!".format(end_point)
                    candidate_words = [get_official_name(word[0]) for word in start_check_is_correct]
                
                elif len(start_check_is_correct) == 1 and len(end_check_is_correct) > 1:
                    stage = set_stage(uid, 34)
                    start_point = set_start_point(uid, get_official_name(start_check_is_correct[0][0]))
                    reply = "출발지 역은 {} 이군요! 근데 도착역은 어디이신가요? 아래의 보기에서 알려주세요!".format(start_point)
                    candidate_words = [get_official_name(word[0]) for word in end_check_is_correct]

                # -> stage 3로 처리
                else:
                    stage = set_stage(uid, 3)
                    reply = "역 이름을 잘 모르겠어요 T.T 출발지 역부터 다시 말해주세요!"
                    candidate_words = [get_official_name(word[0]) for word in start_check_is_correct]
                    set_end_point(uid, end_point) # 오타난 단어 일단 DB에 저장

        # 띵톡 호출 후, "경로 내", "최단 경로", "최소 환승" 입력한 경우 첫 입력 =========
        # ===========================================================================


        # [3] 메시지 하나씩 받아오기 - 띄엄띄엄 보내는 경우 ===============
        elif stage == 3:

            if txt == "없음":
                reply = "'A역'과 같이 출발지 역부터 다시 말해주세요!"

            else:
                # station = extract_station_name(txt)
                station = txt
                if station[-1] == '역' and station != "서울역": station = station[:-1]
                check_is_correct = correct_subway_word(station)

                if len(check_is_correct) == 1:
                    # if not completed_get_start_point:
                    
                    start_point = set_start_point(uid, get_official_name(check_is_correct[0][0]))
                    end_point = replace_num_eng_to_korean(get_end_point(uid))
                    stage = set_stage(uid, 34)
                    if not len(end_point): 
                        reply = "출발지역은 {} 이군요! 그럼 이제 도착지역을 'A역'과 같이 다시 입력해 주세요!".format(start_point)
                    else:
                        end_check_is_correct = correct_subway_word(end_point)
                        reply = "도착지역과 유사한 단어들을 찾아보았어요! 해당하는 단어 중 찾으시는 역명을 골라주세요!"
                        candidate_words = [get_official_name(word[0]) for word in end_check_is_correct]
                else:
                    reply = "출발지역과 유사한 단어들을 찾아보았어요! 해당하는 단어 중 찾으시는 역명을 골라주세요!"
                    candidate_words = [get_official_name(word[0]) for word in check_is_correct]
        # [3] 메시지 하나씩 받아오기 - 띄엄띄엄 보내는 경우 ===============

        # [4] 출발/도착지 모두 확인한 경우 ===============================
        elif stage == 4:
            
            if "방법" in txt:   # 최단 시간 방법, 최소 환승 방법인 경우(stage=1 이후)
                stage = set_stage(uid, 6) if txt == "최단 시간 방법" else set_stage(uid, 7)
                Sopt = 1 if txt == "최단 시간 방법" else 2

                # 출발역과 도착역 불러오기
                start_point = replace_num_eng_to_korean(get_start_point(uid))
                end_point = replace_num_eng_to_korean(get_end_point(uid))
                # DB에 맞는 역명 -> code로 변환
                SID, EID = from_name_to_code(start_point, end_point)

                # 오디세이 호출
                odsay_json = get_odsay_API(SID=SID, EID=EID, Sopt=Sopt)
                # print("odsay_json: ", odsay_json)
                station_list, toilet_here = list(), list()
                toilet_loc = dict() 
                total_time = extract_total_time(odsay_json)
                detailed_routine = extract_show_routine(odsay_json)
                routine_ID = extract_routine_ID(odsay_json)

                station_list.append(detailed_routine[0]) 
                code_intoilet = check_isintoilet_by_code(extract_exact_start_code(odsay_json)) 
                if code_intoilet: toilet_here.append( [detailed_routine[0]] + code_intoilet )


                for i in range(1, len(detailed_routine)):
                    each_station = detailed_routine[i]
                    station_list.append(each_station)
                    code_intoilet = check_isintoilet_by_code(routine_ID[i-1])
                    if code_intoilet and not len(toilet_here) == 3: toilet_here.append( [each_station] + code_intoilet )

                for i in range(len(toilet_here)):
                    _, _, detailed = toilet_here[i] 
                    if len(detailed) >= 60: toilet_here[i][2] = detailed[:57] + "..."
                stage = set_stage(uid, 5)

            elif txt == "출발역 틀림":
                stage = set_stage(uid, 33)
                reply = "출발역을 다시 한 번 입력해 주세요."

            elif txt == "도착역 틀림":
                stage = set_stage(uid, 34)
                reply = "도착역을 다시 한 번 입력해 주세요."

            elif txt == "역이 전부 틀림":
                stage = set_stage(uid, 3)
                reply = "출발역 부터 다시 입력해 주세요. \n'A역'과 같이 역 이름을 말씀해주세요!"
            
            elif txt == "다 맞음":  # 경로 찾는 서비스인 경우(stage=21 or 22 이후)
                last_stage = get_last(uid)
                Sopt = 1 if last_stage == '21' else 2

                # 출발역과 도착역 불러오기
                start_point = replace_num_eng_to_korean(get_start_point(uid))
                end_point = replace_num_eng_to_korean(get_end_point(uid))
                # DB에 맞는 역명 -> code로 변환
                SID, EID = from_name_to_code(start_point, end_point)
                # 오디세이 호출
                odsay_json = get_odsay_API(SID=SID, EID=EID, Sopt=Sopt)

                station_list = list() 
                detailed_routine = extract_show_routine(odsay_json)
                total_time = extract_total_time(odsay_json)
                exchange_list = extract_exchange_info(odsay_json)
                for each_station in detailed_routine: station_list.append(each_station)

                # 환승구간이 없을 경우, start에 호선 정보 추가.
                if len(exchange_list) == 0:
                    start_code = extract_exact_start_code(odsay_json)
                    line_name = get_line_name(start_code)
                    start_point = [start_point, line_name]

                route_result = station_list
                stage = set_stage(uid, 23)
                # initialize(uid)
        # [4] 출발/도착지 모두 확인한 경우 ===============================


        # [10] 특정역 처리 =====================================================
        elif stage == 10 or stage == 19:
            # stage 조정
            set_last(uid, stage)

            station = extract_station_name(txt)
            station_is_correct = correct_subway_word(station)
            if station[-1] == '역' and station != "서울역": station = station[:-1]
            if station_is_correct[0][1] == 0:
                if check_one_isintoilet(station):
                    station = get_official_name(station)
                    reply = "{station_name}에는 개찰구 내 화장실이 있습니다.".format(station_name=station)
                else:
                    station = get_official_name(station)
                    reply = "{station_name}에는 개찰구 내 화장실이 없습니다.".format(station_name=station) 
                initialize(uid)
                stage = set_stage(uid, 19)
            else:
                stage = set_stage(uid, 11)
                reply = "유사한 단어들을 찾아보았어요! 해당하는 단어 중 찾으시는 역명을 골라주세요!"
                candidate_words = [get_official_name(word[0]) for word in station_is_correct]
            
        # [10] 특정역 처리 =====================================================

        # ==========================================================
        # 예외 Case 처리 ============================================
        elif stage == 11:
            if txt == "없음":
                reply = "다시 알려 주실수 있을까요??ㅠㅠ\n'A역'과 같이 역 이름만 말씀해주세요! 개찰구 안에 화장실이 있는지 알려드릴게요."
                stage = set_stage(uid, 10)
            else:
                station = replace_num_eng_to_korean(txt)         
                if check_one_isintoilet(station):
                    station = get_official_name(station)
                    reply = "{station_name}에는 개찰구 내 화장실이 있습니다.".format(station_name=station)
                else:
                    station = get_official_name(station)
                    reply = "{station_name}에는 개찰구 내 화장실이 없습니다.".format(station_name=station) 
                initialize(uid)
                stage = set_stage(uid, 19)
                

        elif stage == 33 or stage == 34:
            if txt == "없음":
                stage = set_stage(uid, stage)
                reply = "역명을 다시 입력해 주세요. \n'A역'과 같이 역 이름을 말씀해주세요!"
            else:
                txt = replace_num_eng_to_korean(txt)
                station_is_correct = correct_subway_word(txt)
                station = txt
                if station[-1] == '역' and station != "서울역": station = station[:-1]
                if station_is_correct[0][1] == 0:
                    if stage == 33: 
                        start_point = set_start_point(uid, get_official_name(station))                 
                        end_point = get_end_point(uid)
                    else: end_point = set_end_point(uid, get_official_name(station))
                    stage = set_stage(uid, 4)
                    last_stage = get_last(uid)
                else:
                    reply = "유사한 역 이름을 찾아보았어요! 밑의 단어 중 찾으시는 역명을 골라주세요!"
                    candidate_words = [get_official_name(word[0]) for word in station_is_correct]

        # stage 별 분기 종료 ======================================================

        # 관련 없는 입력 처리
        else:
            reply = "제가 대답할 수 없는 말이에요 T.T 제가 필요한 상황이라면 이름을 불러주세요~!"
            reply += "Error statue: {stage}, {last_stage}".format(stage=stage, last_stage=get_last(uid))

    return jsonify({
            'message':reply, 
            'stage': stage,
            'last_stage': int(last_stage), 
            'start':start_point, 
            'end':end_point,
            'candidate_words': candidate_words,
            'toilet_here': toilet_here,
            'toilet_loc': toilet_loc,
            'route_result': route_result,
            'total_time': total_time,
            'exchange_list': exchange_list
            })

if __name__ == "__main__":
    app.run(host='0.0.0.0')
