from bs4 import BeautifulSoup
import requests
import urllib.request
import jieba
import pandas as pd
import random
import matplotlib.pyplot as plt
import urllib.parse

score = 0
countword = 0
countpage = 0
all_word = [0,0]  #pos,neg
word = list()
urllist = list()
record = list()
record_title = list()
labels = 'Postive','Negatuve'

'''
user_agents是提供爬蟲進行搜詢時的身分，以免被403
'''

user_agents = [\
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20130406 Firefox/23.0', \
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:18.0) Gecko/20100101 Firefox/18.0', \
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/533 (KHTML, like Gecko) Element Browser 5.0', \
    'IBM WebExplorer /v0.94', \
    'Galaxy/1.0 [en] (Mac OS X 10.5.6; U; en)', \
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)', \
    'Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14', \
    'Mozilla/5.0 (iPad; CPU OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5355d Safari/8536.25', \
    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1468.0 Safari/537.36', \
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0; TheWorld)']

'''
以下的code是將外部的中文情緒字典導入至程式，使程式能進行分析
'''
sentment_table = pd.read_excel('情感词典修改版.xlsx')
sentment_table.drop(['Unnamed: 10','Unnamed: 11'],inplace=True,axis=1)
pos_table = pd.read_excel('情感词典修改版_pos.xlsx')
neg_table = pd.read_excel('情感词典修改版_neg.xlsx')

pos_dict = dict(zip(list(pos_table.posword),list(pos_table.score)))
neg_dict = dict(zip(list(neg_table.negword),map(lambda a:a*(0-1),list(neg_table.score)) ))
sentment_dict={**pos_dict,**neg_dict}

for w in sentment_dict.keys():
    jieba.suggest_freq(w,True)

stop_words =open('stopword.txt',encoding='utf8').readlines()
while(True):
    record_title_func = ''
    record_title_value = ''
    chose_func = int(input("請選取搜尋方法(1.關鍵字 2.URL 3.查詢圖表紀錄 0.EXIT):"))
    if chose_func == 1:
        urllist.clear()
        record_title_func = '關鍵字'
        key = input('keyword:')
        record_title_value = key
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
        html = requests.get("https://www.google.com/search?q="+key,headers=headers)
        sp = BeautifulSoup(html.text,"html.parser")
        
        str1 = sp.find_all(class_='r')
        
        for str2 in str1:
            link = str2.find('a')
            urllist.append(link.get('href'))
            
    elif chose_func == 2:
        urllist.clear()
        record_title_func = 'URL'
        url = input('URL:')
        record_title_value = url
        urllist.append(url)
    
    elif chose_func == 3:
        if record != None :
            tag = int(input('輸入查詢紀錄tag:'))
            if tag >len(record) or tag<1:
                print('資料不存在')
                continue
            else:
                print(record_title[tag-1])
                plt.pie(record[tag-1], labels = labels,autopct='%1.1f%%')
                plt.axis('equal')
                plt.show()
        else:
            continue
        continue
    
    elif chose_func == 0:
        break
    
    else:
        print('404 No code of function')
        continue
    
    
    countpage = 1
    for URL in urllist:
        all_word = [0,0]
        score = 0
        countword = 0
        
        print('第',countpage,'筆資料：')
        
        user_agent = random.choice(user_agents)
        reqp = urllib.request.Request(URL)
        reqp.add_header('User-Agent', user_agent)
        response = urllib.request.urlopen(reqp)
        
        html_cont = response.read()
        soup = BeautifulSoup(html_cont,'html.parser',from_encoding='utf-8')
        title = soup.title
        print(title.string)
        print(urllib.parse.unquote(URL))
        content = soup.find_all('p')
        
        for c in content:
            words = jieba.cut(str(c), cut_all=False)
            for w in words: 
                if w not in stop_words:
                    word.append(w)
        
        for i in word:
            if i in sentment_dict.keys():
                if sentment_dict[i] > 0:
                    all_word[0] += 1
                elif sentment_dict[i] < 0:
                    all_word[1] += 1
                    
                score += sentment_dict[i]
                countword += 1
        
    
        print('關鍵字分析：',score)
        print('關鍵字數量：',countword)
       
        if countword != 0:
            print('總評價：',round(score/countword, 2))
        else:
            print(0)
        countpage += 1
        
    record.append(all_word)
    record_title.append('使用'+record_title_func+'搜尋'+record_title_value)
    
    plt.pie(all_word , labels = labels,autopct='%1.2f%%')
    plt.axis('equal')
    plt.show()
