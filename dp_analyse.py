import os
os.environ["CUDA_VISIBLE_DEVICES"]="-1"
import tensorflow
import hanlp
import use_case_diagram
tokenizer = hanlp.load('LARGE_ALBERT_BASE')
tagger = hanlp.load(hanlp.pretrained.pos.CTB9_POS_ALBERT_BASE)
semantic_parser = hanlp.load(hanlp.pretrained.sdp.SEMEVAL16_NEWS_BIAFFINE_ZH)
#如果客户之前用信用卡付款，而其信用卡账户退还交易被拒绝，则告知顾客并使用现金退款。
#摘要：顾客携带所购商品到达收银台，收银员使用pos系统记录每件商品。系统连续显示累计总额，并逐行显示细目。顾客输入支付信息，系统对支付信息进行验证和记录。系统更新库存信息。顾客从系统中得到购物小票，然后携带商品离开。如果客户之前用信用卡付款，而其信用卡账户退还交易被拒绝，则告知顾客并使用现金退款。如果在系统中未查找到该商品的标识码，则提示收银员并建议手工输入标识码。
#学生使用JXG系统查询新学期将开设的课程和授课教师的情况



#toker=tokenizer('收银员使用pos系统记录每件商品')
#系统管理员可以运用的功能，像修改密码，管理学生信息、成绩信息、课程信息、班级信息并且设置权限。

def POS_ana(text):
    toker = tokenizer(text)

    tag = tagger(toker)
    return tag

def DP_ana(text):
    toker=tokenizer(text)
    tag=tagger(toker)

    argu=[]
    for i in range(len(toker)):
        argu.append((toker[i],tag[i]))

    argu = []
    for i in range(len(toker)):
        argu.append((toker[i], tag[i]))

    syntactic_analyse = syntactic_parser(argu)
    return syntactic_analyse

if __name__=="__main__":
    print(use_case_diagram.get_sdp("收银员使用系统记录每个商品"))
# s="智能答复文档生成能够根据代理上传的专利审查相关的文档，智能识别审查意见中创造性、新颖性问题，并根据专利申请书以及审查意见中提到的文档进行智能比较，给出合理的回复，并把回复内容按一定格式生成文档。"
# toker=tokenizer(s)
# print(toker)
# tagger = hanlp.load(hanlp.pretrained.pos.CTB9_POS_ALBERT_BASE)
# tag=tagger(toker)
# print(tag)
#
# argu=[]#########
# for i in range(len(toker)):
#     argu.append((toker[i],tag[i]))
#
# syntactic_parser = hanlp.load(hanlp.pretrained.dep.CTB7_BIAFFINE_DEP_ZH)
# syntactic_analyse=syntactic_parser(argu)
# print(syntactic_analyse)

# #dict_keys(['id', 'form', 'cpos', 'pos', 'head', 'deprel', 'lemma', 'feats', 'phead', 'pdeprel'])
# #id是序号
# #form是词
# #lemma好像也是词
# #cpos是词性
# #head是父节点序号
# #deprel是关系
#
# #只能从子节点找父节点，父节点不知道自己有哪些子节点
# s_index=[]#系统描述的id
#             #s_father_deprel实际上是{系统名：{'Pat': 2, 'Exp': 5}}
#
# #用于保存用例图的数据结构
# #{系统名:{actor:[usecase,usecase],actor:[usecase,usecase]}}
# use_case_dict={}
# for ele in syntactic_analyse:
#     if ele["deprel"]=="dobj":
#         use_case_dict[ele["head"]]=ele["id"]
# print(use_case_dict)

