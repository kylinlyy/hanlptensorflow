import re
import pdfplumber
import hanlp
import pandas as pd
import dp_analyse
import docx
tokenizer = hanlp.load('LARGE_ALBERT_BASE')
tagger = hanlp.load(hanlp.pretrained.pos.CTB9_POS_ALBERT_BASE)
semantic_parser = hanlp.load(hanlp.pretrained.sdp.SEMEVAL16_NEWS_BIAFFINE_ZH)



def input_pdf(path):
    '''
    读取pdf文件，返回列表，每个元素是一页的内容
    :param path:
    :return:
    '''
    fulltext = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            #print("text:",text)
            #text = text.replace(" ", "")
            fulltext.append(text)
    return fulltext

def pre_process(fulltext):
    '''
    处理fulltext，去掉空字符，用句号把句子分开
    :param fulltext:
    :return:
    '''
    text_without_None = []
    #text_list = re.split(r';|；|:|：|。', fulltext)

    text_list = re.split(r'。', fulltext)
    for ele in text_list:
        if ele != None and ele != "":
            text_without_None.append(ele)
    return text_without_None

def VVNN(text_without_None):
    '''
    找到所有VVNN组合
    :param text_without_None:
    :return:
    '''
    VVNN_list = []
    for e in text_without_None:
        toker = tokenizer(e)
        tag = tagger(toker)

        for i in range(len(tag) - 1):

            if tag[i] == "VV" and tag[i + 1] == "NN":
                VVNN_list.append(toker[i] + toker[i + 1])
    return VVNN_list
        # table = page.extract_tables()
        # for t in table:
        #     # 得到的table是嵌套list类型，转化成DataFrame更加方便查看和分析
        #     df = pd.DataFrame(t[1:], columns=t[0])
        #     print(df)

def input_doc(path):
    '''
    读取word文档，返回字符串
    :param path:
    :return:
    '''
    fulltext=""
    file=docx.Document(path)

    for para in file.paragraphs:
        fulltext+=para.text
    return fulltext

def find_catalogue(fulltext):
    '''

    :param fulltext:
    :return:
    '''
    for page in fulltext:
        if "目录" in page:
            return page

def get_catalogue_dict(cat_pag):
    pag_list=cat_pag.split("\n")
    pag_cat_dict={}
    for pag in pag_list:
        seqenc = ""
        content=""
        i=0
        if not pag[0].isdigit():
            pass
        else:
            while i < len(pag):
                if not '\u4e00' <= pag[i] <= '\u9fff' :
                    seqenc += pag[i]
                    i += 1
                else:
                    j = i
                    while j < len(pag) and pag[j] != ".":
                        content += pag[j]
                        j = j + 1
                    break
        if seqenc!="":
            pag_cat_dict[seqenc]=content
    print("pag_cat_dict:",pag_cat_dict)
    return pag_cat_dict

def get_cat_function(cat_dict):
    function_key=[]
    for k,v in cat_dict.items():
        if "功能" in v and "非功能" not in v:
            return k

#获取功能需求的所有小标题
def filter_empty(f_list):
    while " " in f_list:
        f_list.remove(" ")

def get_function_list(cat_dict,function_key):
    #function_key是指有“功能”字眼的题目
    f_k_list=function_key.split(".")
    filter_empty(f_k_list)
    belong_dict={}
    for k,v in cat_dict.items():
        k_list=k.split(".")
        filter_empty(k_list)
        if len(k_list)>len(f_k_list):
            is_belong = 1  # 1表示属于

            for i in range(len(f_k_list)):
                if k_list[i]==f_k_list[i]:
                    pass
                else:
                    is_belong=0
            if is_belong==1:
                belong_dict[k]=v
    return belong_dict
#def identify_subtitle(fulltext):

'''
正文切分思路
1.目录之后所有文本连成一个字符串
2.用换行符切分
par_list用来记录当前
3.每一行，如果是用数字开头，就判断一下属不属于某个小标题，如果属于，那么之前的
'''

def content_str_2_list(pag_cat_dict):
    #将目录字典，转化为{长度：[[1],[2]],长度:[[1,1],[1,2]]
    cat_list = list(pag_cat_dict.keys())
    cat_ana_dict = {}  # 例如{1: [['1'], ['2'], ['3']], 2: [['1', '1'], ['1', '2'], ['1', '3'], ['2', '1'], ['2', '2'], ['2', '3']], 3: [['2', '2', '1'], ['2', '2', '2'], ['2', '3', '1'], ['2', '3', '2'], ['2', '3', '3']]}
    for cl in cat_list:
        cl_list = cl.split(".")
        filter_empty(cl_list)
        cllen = len(cl_list)
        if cllen in cat_ana_dict.keys():
            cat_ana_dict[cllen].append(cl_list)
        else:
            cat_ana_dict[cllen] = [cl_list]
    return cat_ana_dict

def text_split(v_list,text_list,pag_cat_dict):
    text_dict={}#{1:[text,text],2:[text,text]}
    for i in range(len(v_list)-1):

        vtextlist = []
        v=v_list[i]
        vstr=".".join(v)
        vstr+="."
        #cat_content = pag_cat_dict[vstr]
        vstr2=".".join(v_list[i+1])
        vstr2 += "."
        #cat_content2 = pag_cat_dict[vstr2]
        is_belong=0
        for t in text_list:
            t=t.strip()
            if is_belong==1:
                if t.startswith(vstr2) :
                    break
                else:
                    vtextlist.append(t)
            else:
                if t.startswith(vstr) :
                    is_belong = 1
                    vtextlist.append(t)
        text_dict[vstr]=vtextlist
    vstr=".".join(v_list[-1])
    vstr+="."
    is_belong = 0
    vtextlist=[]
    for t in text_list:
        t = t.strip()
        if is_belong == 1:
                vtextlist.append(t)
        else:
            if t.startswith(vstr):
                is_belong = 1
                vtextlist.append(t)
    text_dict[vstr] = vtextlist

    return  text_dict

def split_fulltext(pag_cat_dict,fulltext):
    #首先要把目录页从fulltext当中去掉
    for page in fulltext:
        if "目录" in page:
            fulltext.remove(page)

    full_text_string="".join(fulltext)
    new_fulltext_list=full_text_string.split("\n")
    full_text_dict={}#用于记录最后输出结果{序号：内容}
    #最大的标题到最小的标题，先切分最短的，从1.开始找，找到2.或者结尾结束
    #中间一直按照列表格式储存
    cat_ana_dict=content_str_2_list(pag_cat_dict)

    #根据cat_ana_dict切分正文
    splited_dict={}
    for k,v in cat_ana_dict.items():
        result=text_split(v,new_fulltext_list,pag_cat_dict)
        splited_dict[k]=result
    return splited_dict
    #result=text_split(cat_ana_dict[1],new_fulltext_list,pag_cat_dict)
    # for ele,v in splited_dict.items():
    #     print(ele)
    #     for k,v1 in v.items():
    #         print("split_fulltext:",k,v1)
    # for k,v in cat_ana_dict:
    #     pass

def get_function_text(f_k,splited_dict):
    '''
    获取功能描述正文
    :param f_k: 功能描述章节序号（str格式）
    :param splited_dict: 正文切分结果字典
    :return:
    '''
    #判断f_k有几位
    f_k_list=f_k.split(".")
    filter_empty(f_k_list)

    level_number=len(f_k_list)
    level_text=splited_dict[level_number]
    f_k=f_k.strip()
    function_text=level_text[f_k]
    return function_text

def extract_possible_usecase(function_text_list):
    '''
    从功能需求描述正文（列表格式）中提取去可能作为用例的短语
    1.先找到最长的元素，一般来讲这是整一行的长度
    2.提取出所有长度不满足的元素
    3.这就有可能是
    :param function_text_list:
    :return:
    '''
    max_length=0
    possible_usecase_list=[]
    for text in function_text_list:
        l=len(text)
        if l>max_length:
            max_length=l
    max_length=max_length-3
    for text in function_text_list:
        if len(text)<max_length:

            possible_usecase_list.append(text)
    return possible_usecase_list

def has_chinese(string):
    for ch in string:
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
    return False

def has_english(string):
    for ch in string:
        if ch.isalpha():
            return True
    return False

def judge_usecase(possible_usecase_list):
    '''
    初步判断是不是用例，根据长度，符号等
    :param possible_usecase_list:
    :return:
    '''
    usecase=[]
    for posuse in possible_usecase_list:
        #去掉前后的非中文字符
        posuse = posuse.strip()
        posuse=posuse.strip("）")
        #posuse中不可能有逗号、句号
        if "，" in posuse or "。" in posuse:
            pass
        else:
            if posuse!="" :
                if has_chinese(posuse) or has_english(posuse):
                    usecase.append(posuse)
    return usecase

def judge_usecase2(posuse_list,function_text):
    function_string="".join(function_text)
    has_chinese

#fulltext=input_doc("data\\ligang\\AI专利审查意见答复辅助系统项目用户需求.docx")
fulltext=input_pdf("data\\ligang\\AI专利审查意见答复辅助系统项目用户需求.pdf")
#result=pre_process(fulltext)
cat_pag=find_catalogue(fulltext)
cat_dict=get_catalogue_dict(cat_pag)
splited_dict=split_fulltext(cat_dict,fulltext)#切分全文
f_k=get_cat_function(cat_dict)#找到功能描述的章节（只是序号）
result=get_function_list(cat_dict,f_k)
function_text=get_function_text(f_k,splited_dict)#通过f_k(功能描述章节的序号）和splited_dict章节序号和具体内容对应的字典，得到具体的功能描述文本
possible_usecase_list=extract_possible_usecase(function_text)
#print(function_text)
posuse=judge_usecase(possible_usecase_list)
print("posuse:",posuse)