#coding=utf8
import os
os.environ["CUDA_VISIBLE_DEVICES"]="-1"

import hanlp
tokenizer = hanlp.load('LARGE_ALBERT_BASE')
tagger = hanlp.load(hanlp.pretrained.pos.CTB9_POS_ALBERT_BASE)
syntactic_parser = hanlp.load(hanlp.pretrained.dep.CTB7_BIAFFINE_DEP_ZH)
usecase_desc="顾客携带所购商品到达收银台，收银员使用pos系统记录每件商品。系统连续显示累计总额，并逐行显示细目。顾客输入支付信息，系统对支付信息进行验证和记录。系统更新库存信息。顾客从系统中得到购物小票，然后携带商品离开。如果客户之前用信用卡付款，而其信用卡账户退还交易被拒绝，则告知顾客并使用现金退款。如果在系统中未查找到该商品的标识码，则提示收银员并建议手工输入标识码。"

system_Desc=["系统","软件"]

def split_sentence(paragraph):
    '''
    将段落分成句子
    :param sentence: 要被划分的段落
    :return: 划分好的句子列表
    '''
    sentence_juhao=paragraph.split("。")
    sentence_douaho=[]
    for j in sentence_juhao:
        sentence_douaho=sentence_douaho+j.split("，")
    sentence_fenhao=[]
    for d in sentence_douaho:
        sentence_fenhao=sentence_fenhao+d.split("；")
    return sentence_fenhao

def get_sdp(sentence):
    '''
    获得句子的语义分析结果
    :param sentence:
    :return:
    '''
    toker = tokenizer(sentence)
    tag = tagger(toker)
    argu = []
    for i in range(len(toker)):
        argu.append((toker[i], tag[i]))
    e1 = syntactic_parser(argu)
    print(e1)

if __name__=="__main__":
    sen=split_sentence(usecase_desc)
    for s in sen:
        get_sdp(s)

