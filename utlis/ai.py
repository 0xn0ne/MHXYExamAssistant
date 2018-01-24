import requests, time, _thread, re
from urllib.parse import urlparse
import config
from difflib import SequenceMatcher
from bs4 import BeautifulSoup
# from model import Question

class Ai:

    def __init__(self, issue, answers):
        self.answers = {}
        self.result = {}
        self.issue = issue
        for i in answers:
            self.answers[i] = 0
        self.finish_count = 0

    # def db_search(self):
    #     issue = ''
    #     for i in self.issue:
    #         issue += i + '%'
    #     issue = '%' + issue
    #     print(issue)
    #     print(Question.search_by_q(issue))
    #     print(Question.get_by_q(self.issue).question)

    def gethtml(self, url, engine):
        headers = {
            'Upgrade-Insecure-Requests': 1,
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'
        }

        html_doc = requests.get(url).text
        soup = BeautifulSoup(html_doc, 'html.parser')
        a = []
        ex = False
        self.clear = ''
        try:
            for i, j in enumerate(soup.find_all("div", class_="c-abstract")):
                for z in self.answers:
                    r = re.search(r'[%s].*?[%s]+' % (self.issue, z), j.get_text())
                    try:
                        c = SequenceMatcher(None, r.group(0), f'{self.issue} {z}').quick_ratio()
                        a.append([c, j.get_text()])
                        if c > 0.9:
                            ex = True
                            break
                    except AttributeError:
                        pass
                if ex:
                    break
            self.clear = sorted(a, key=lambda k:k[0], reverse=True)[:4]

            self.result[engine] = self.answers
            for i in self.clear:
                for j in self.answers:
                    self.result[engine][j] += i[1].count(j)
        except Exception:
            print('近期发现OCR无法识别数字答案，导致搜索失败，请检测OCR是否已正常识别')
            pass

        self.finish_count += 1

    def tell_me_result(self):
        for i in config.SEARCH_ENGINE:
            thr = _thread.start_new_thread(self.gethtml, (i.format(f'梦幻西游手游 {self.issue}'), urlparse(i)[1] + '/MHXY'))
            thr = _thread.start_new_thread(self.gethtml, (i.format(self.issue), urlparse(i)[1]))

        while True:
            time.sleep(0.1)
            if self.finish_count >= len(config.SEARCH_ENGINE) * 2:
                break
        return self.result, self.clear


__all__ = ['Ai']

if __name__ == '__main__':
    # a = Ai('甲骨文出现在哪个朝代', ['夏朝', '唐朝', '商朝', '汉朝'])
    # a = Ai('哪一张变化之术克制青苍?', ['黄莽', '赤炎', '赤红', '炎黄'])
    # a = Ai('太阳系最亮的星星是哪一颗?', ['火星', '金星', '木星', '水星'])
    a = Ai('频道里大家通常喊的“一条”不包括', ['普通副本', '捉鬼', '押送高级镖银', '封妖'])
    print(a.tell_me_result())