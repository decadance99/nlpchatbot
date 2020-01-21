from flask_EC2.typing_error_processing import jamo_levenshtein, decompose
import json

data = open("./flask_EC2/data/subway_dict.json", 'r', encoding='utf-8')

subway_Dict = json.load(data)

def _find_most_similar_in_group(word, search_words):
    
    len_search_words = len(search_words)
    if len_search_words == 1: return [ (search_words[0], jamo_levenshtein(word, search_words[0])) ]

    score_list = []
    for elem in search_words:
        dist = jamo_levenshtein(word, elem)
        score_list.append( (elem, dist) )


    score_list.sort(key=lambda x: x[1])
    if len_search_words <= 5: return score_list
    else: return score_list[:5]


def correct_subway_word(word):
    if len(word) == 0: return list() 

    if word[-1] == "역" and not word =="서울역": word = word[:-1]
    # 첫 글자를 우선순위로 유사한 역명 찾는 방법.
    first_char = word[0]
    if first_char in subway_Dict:   # 첫 글자로 시작하는 모든 역명 return
        cur_search_words = subway_Dict[first_char]
        return_list = _find_most_similar_in_group(word, cur_search_words)
    else:
        # 첫 글자와 일치하는 역명이 없을 경우, 초성 단위로 분해 후, 비슷한 역명 찾는 방법.
        chosung_word = decompose(first_char)[0]
        item_list = [item for item in subway_Dict if decompose(item)[0] == chosung_word]

        most_similar_item = [(item, jamo_levenshtein(first_char, item)) for item in item_list]
        most_similar_item.sort(key=lambda x: x[1])

        substitute_words = []
        for i in range(10):
            if i == len(most_similar_item): break
            substitute_words += subway_Dict[ most_similar_item[i][0] ]
        return_list = _find_most_similar_in_group(word, substitute_words)
    
    if return_list[0][1] == 0: return return_list[:1]
    else: return return_list