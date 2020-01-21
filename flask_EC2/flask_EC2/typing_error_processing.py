# -*- encoding:utf8 -*-
import sys  

kor_begin = 44032
kor_end = 55203
chosung_base = 588
jungsung_base = 28
jaum_begin = 12593
jaum_end = 12622
moum_begin = 12623
moum_end = 12643

chosung_list = [ 'ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 
        'ㅅ', 'ㅆ', 'ㅇ' , 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']

jungsung_list = ['ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 
        'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ', 'ㅙ', 'ㅚ', 
        'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 
        'ㅡ', 'ㅢ', 'ㅣ']

jongsung_list = [
    ' ', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ',
        'ㄹ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 
        'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 
        'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']

jaum_list = ['ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄸ', 'ㄹ', 
              'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 
              'ㅃ', 'ㅄ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']

moum_list = ['ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ', 
              'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ']

# first, mid, end == 초성, 중성, 종성
def compose(chosung, jungsung, jongsung):
    char = chr(
        kor_begin + 
        chosung_base + chosung_list.index(chosung) + 
        jungsung_base + jungsung_list.index(jungsung) + 
        jongsung_list.index(jongsung)
    )
    return char

def _is_character_Korean(char):
    i = ord(char)
    return (
        (kor_begin <= i <= kor_end) or
        (jaum_begin <= i <= jaum_end) or
        (moum_begin <= i <= moum_end)
    )

def decompose(char):
    i = _to_base(char)
    if (jaum_begin <= i <= jaum_end):
        return (char, ' ', ' ')

    if (moum_begin <= i <= moum_end):
        return (' ', char, ' ')    
    
    i -= kor_begin
    chosung = i // chosung_base
    jungsung = (i - chosung*chosung_base) // jungsung_base
    jongsung = (i - chosung*chosung_base - jungsung*jungsung_base)
    return (chosung_list[chosung], jungsung_list[jungsung], jongsung_list[jongsung])

def _to_base(c):

    if type(c) == str or type(c) == int: return ord(c)
    else: raise TypeError

def levenshtein(s1, s2, cost={}):
    # based on Wikipedia/Levenshtein_distance#Python
    if len(s1) < len(s2): return levenshtein(s2, s1)
    if len(s2) == 0: return len(s1)
    def get_cost(c1, c2, cost): return 0 if (c1 == c2) else cost.get((c1, c2), 1)
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1 # j+1 instead of j since previous_row and current_row are one character longer
            deletions = current_row[j] + 1       # than s2
            substitutions = previous_row[j] + get_cost(c1, c2, cost)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]

def jamo_levenshtein(s1, s2):
    if len(s1) < len(s2): return jamo_levenshtein(s2, s1)

    if len(s2) == 0: return len(s1)
    
    def get_jamo_cost(c1, c2): return 0 if (c1 == c2) else levenshtein(decompose(c1), decompose(c2))/3

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1 # j+1 instead of j since previous_row and current_row are one character longer
            deletions = current_row[j] + 1       # than s2
            substitutions = previous_row[j] + get_jamo_cost(c1, c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]

