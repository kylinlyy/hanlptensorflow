import re
import pdfplumber
import hanlp
import pandas as pd
import use_case_diagram
import docx
import read_pdf_text
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
    tables=[]
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            table=page.extract_tables()
            if len(table)>0:
                tables.append(table)
            fulltext.append(text)
    return fulltext,tables

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
    print("fulltext:",fulltext)
    line_list=[]
    for tex in fulltext:
        tex_list=tex.split("\n")
        line_list+=tex_list
    cat_list=[]
    for l in line_list:
        if re.match("^[0-9][0-9\.]*\s*[a-zA-Z\u4e00-\u9fa5]+\s*\.+\s*[0-9]+$",l):
            cat_list.append(l)
    if len(cat_list)>0:
        page="\n".join(cat_list)
    else:
        page=None

    # pattern = re.compile(r'目\s*录')
    #
    # for page in fulltext:
    #     print("page:",page)
    #     linelist=page.split("\n")
    #     for line in linelist:
    #         if pattern.match(line):
    #             return page
    return page
def get_catalogue_dict(cat_pag):

    pag_list=cat_pag.split("\n")
    filter_empty(pag_list)
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
    while "" in f_list:
        f_list.remove("")

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
    pattern = re.compile(r'目\s*录')
    for page in fulltext:
        linelist = page.split("\n")
        for line in linelist:
            if pattern.match(line) :
                fulltext.remove(page)
                break
    print("fulltext:",fulltext)
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
    print("splited_dict:",splited_dict)
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
    初步判断是不是用例，根据长度，符号等，相当于预处理
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
                #必须有中文或者英文才是用例
                if has_chinese(posuse) or has_english(posuse):
                    usecase.append(posuse)
    return usecase

def join_pdf_text(pdf_list):
    #根据长度，不满足一行的，不和下一行合并
    max_length=0
    for pl in pdf_list:
        lpl=len(pl)
        if max_length<lpl:
            max_length=lpl
    result_list=[]
    add_str = ""
    for pl in pdf_list:
        if len(pl)<max_length-3:
            add_str+=pl
            result_list.append(add_str)
            add_str=""
        else:
            add_str+=pl
    result_list.append(add_str)

    return result_list

def judge_usecase2(posuse_list,function_text):
    #从语义层面进行判断。
    #首先把相关的语句都添加到posuse_dict里面
    #返回所有可能用例和所有包含用例的语句
    '''
    1.去掉只包含用例本身的，例如{整车供应链：[整车供应链]}
    :param posuse_list:
    :param function_text:
    :return:
    '''
    functiong_l=join_pdf_text(function_text)
    posuse_dict={}#{疑似用例：[语句，语句]}
    for fl in functiong_l:
        fl=fl.strip()
        fl=fl.strip("）")
        for posuse in posuse_list:
            if posuse in fl and posuse!=fl:
                if posuse in posuse_dict.keys():
                    posuse_dict[posuse].append(fl)
                else:
                    posuse_dict[posuse]=[fl]
    return posuse_dict

def DP_ana(use_case,use_case_sentence):
    uc_sentence=use_case_sentence.replace(use_case,"它")
    DP_result=use_case_diagram.get_sdp(uc_sentence)
    return DP_result

def choose_real_uc(posuse_dict):
    for k,v in posuse_dict.items():
        for sen in v:
            DP_result=DP_ana(k,sen)
            #mmod是情态动词，使，能够这是一种情况
            #收集其他的做分类？
            #如果：“它”是nsubj，下一个是mmod，就是它能
            #如果：“
            print(DP_result)

def posuse_pre_process(posuse_list):
    '''
    输入是posuse_dict的一个元素的值
    :param posuse_list:
    :return:
    '''

def get_function_table(tables):
    '''
    针对李刚老师公司文档
    :param tables:
    :return:
    '''
    function_table=[]

    for table in tables:
        if "功能类别" in table[0][0] and "子功能" in table[0][0]:
            function_table=table[0]
    print(function_table)
    return function_table

def get_usecase_table(function_table):
    '''
    专门解决李刚老师公司文档，从表格中提取功能
    :param function_table:
    :return:
    '''
    function_dict={}
    key_now=""
    for i in range(1,len(function_table)):
        if function_table[i][0]!=None:
            key_now = function_table[i][0]
            function_dict[key_now]=[function_table[i][1]]
        else:
            function_dict[key_now].append(function_table[i][1])
    return function_dict

#fulltext=input_doc("data\\ligang\\AI专利审查意见答复辅助系统项目用户需求.docx")
if __name__=="__main__":
    fulltext,tables = input_pdf("data\\fromInternet\\《劝学》 一课多媒体课件开发系统.pdf")
    fulltext=read_pdf_text.parse("data\\fromInternet\\《劝学》 一课多媒体课件开发系统.pdf")
    function_table=get_function_table(tables)
    function_dict=get_usecase_table(function_table)
    print("function_dict:",function_dict)
    # result=pre_process(fulltext)
    cat_pag = find_catalogue(fulltext)

    cat_dict = get_catalogue_dict(cat_pag)
    splited_dict = split_fulltext(cat_dict, fulltext)  # 切分全文
    f_k = get_cat_function(cat_dict)  # 找到功能描述的章节（只是序号）
    result = get_function_list(cat_dict, f_k)
    function_text = get_function_text(f_k, splited_dict)  # 通过f_k(功能描述章节的序号）和splited_dict章节序号和具体内容对应的字典，得到具体的功能描述文本
    possible_usecase_list = extract_possible_usecase(function_text)
    # print(function_text)
    posuse = judge_usecase(possible_usecase_list)
    posuse_dict = judge_usecase2(posuse, function_text)
    for k, v in posuse_dict.items():
        print(k, v)
    choose_real_uc(posuse_dict)
