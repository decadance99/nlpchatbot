
# ec2에서 odsay를 통한 각 역의 고유 코드 호출 및 csv file로 저장.

import requests
import csv

def readCSV(path):
    data = open(path, 'r', encoding='utf-8')

    extractData = list()
    skip_title = True
    for lines in data:
        if skip_title:
            skip_title = False
            continue
        elem = lines.split(",")
        name, line = elem[1], elem[3]

        # 서울공공빅데이터와 odsay의 전철 라인명 통일 ==================
        if line[0] == '0':
            line = line[1:]
        elif line == '경의선':
            line = '경의중앙선'
        elif line == '인천선':
            line = '인천 1호선'
        elif line == '인천2호선':
            line = '인천 2호선'
        elif line == '용인경전철':
            line = '에버라인'
        elif line == '서해선':
            line = '서해선(소사-원시)'
        # ============================================================
        extractData.append( [name, line] )
    
    return extractData

def writeCSV(path, writeData):
    data = open(path, 'w', encoding='utf-8', newline='')
    wr = csv.writer(data)
    for line in writeData:
        wr.writerow(line)
    data.close()
    return True

def get_odsay_API(name, line):

    API_KEY = 'aOL47WqSS5JZuMY8n7TXU0vvvYRMh5XjleXt7IXEClI'

    # params:
    # {name} = 검색할 정류장 이름
    # {CID} = 도시 코드(1000: 수도권)
    # {stationCalss} = 정류장 종류(2: 지하철 역)
    # {apiKey} = api key

    openApiURL = 'https://api.odsay.com/v1/api/searchStation?lang=0&stationName={name}&CID=1000&stationClass=2&apiKey={API_KEY}'.format(name=name, API_KEY=API_KEY)
    openApiURL = openApiURL.encode(encoding='UTF-8')
    response = requests.get(openApiURL)

    rsp_json = response.json()
    print("rsp_json: ", rsp_json)

    # 검색결과 없을 경우 ==========================
    if rsp_json is None:
        return -1
    # ============================================

    stationResult = rsp_json['result']['station']

    # odsay 호출 결과 같은 호선인지 확인(같은 역, 다른 라인일 경우 코드가 다름)
    for elem in stationResult:
        stationLane = elem['laneName']
        if '수도권' in stationLane:
            stationLane = stationLane[4:]
        if line != stationLane:
            continue
        else:
            stationName = elem['stationName']
            stationID = elem['stationID']
            # 역이름, 역 라인명이 같은 경우 코드와 함께 return
            return [stationName, stationLane, stationID]
    
    return -1

if __name__ == "__main__":

    path = "./subwayInfo.csv"
    csv_data = readCSV(path)
    success_list = []
    failed_list = []

    # For a test 
    for i in range( len(csv_data) ):
        name = csv_data[i][0]
        line = csv_data[i][1]
        print("status: %d => %s, %s" % (i+1, name, line) )
        odsay_found_result = get_odsay_API(name, line)
        if odsay_found_result == -1:
            print("failed case: ", name, line)
            failed_list.append( [name, line] )
        else:    
            success_list.append(odsay_found_result)

    print("success case number: ", len(success_list))
    print("Failed list: ", failed_list)

    writeCSV("./success_list.csv", success_list)
    writeCSV("./failed_list.csv", failed_list)

    print("saved with csv files")




