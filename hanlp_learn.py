import os
os.environ["CUDA_VISIBLE_DEVICES"]="-1"
import tensorflow
import hanlp
tokenizer = hanlp.load('LARGE_ALBERT_BASE')
tagger = hanlp.load(hanlp.pretrained.pos.CTB9_POS_ALBERT_BASE)
semantic_parser = hanlp.load(hanlp.pretrained.sdp.SEMEVAL16_NEWS_BIAFFINE_ZH)
#如果客户之前用信用卡付款，而其信用卡账户退还交易被拒绝，则告知顾客并使用现金退款。
#摘要：顾客携带所购商品到达收银台，收银员使用pos系统记录每件商品。系统连续显示累计总额，并逐行显示细目。顾客输入支付信息，系统对支付信息进行验证和记录。系统更新库存信息。顾客从系统中得到购物小票，然后携带商品离开。如果客户之前用信用卡付款，而其信用卡账户退还交易被拒绝，则告知顾客并使用现金退款。如果在系统中未查找到该商品的标识码，则提示收银员并建议手工输入标识码。
#学生使用JXG系统查询新学期将开设的课程和授课教师的情况
# toker=tokenizer('顾客携带所购商品到达收银台')
# print(toker)
#
# tag=tagger(toker)
# print(tag)
#
# #syntactic_parser = hanlp.load(hanlp.pretrained.dep.CTB7_BIAFFINE_DEP_ZH)
#
# argu=[]
# for i in range(len(toker)):
#     argu.append((toker[i],tag[i]))
# # semantic_parser = hanlp.load(hanlp.pretrained.sdp.SEMEVAL16_NEWS_BIAFFINE_ZH)
# e1=semantic_parser(argu)
# print(e1)


#toker=tokenizer('收银员使用pos系统记录每件商品')
#系统管理员可以运用的功能，像修改密码，管理学生信息、成绩信息、课程信息、班级信息并且设置权限。
toker=tokenizer('收银员使用pos系统记录每件商品')
print(toker)
tagger = hanlp.load(hanlp.pretrained.pos.CTB9_POS_ALBERT_BASE)
tag=tagger(toker)
print(tag)

argu=[]#########
for i in range(len(toker)):
    argu.append((toker[i],tag[i]))
e1=semantic_parser(argu)
print(e1)
syntactic_parser = hanlp.load(hanlp.pretrained.dep.CTB7_BIAFFINE_DEP_ZH)
print(syntactic_parser(argu))
#dict_keys(['id', 'form', 'cpos', 'pos', 'head', 'deprel', 'lemma', 'feats', 'phead', 'pdeprel'])
#id是序号
#form是词
#lemma好像也是词
#cpos是词性
#head是父节点序号
#deprel是关系

#只能从子节点找父节点，父节点不知道自己有哪些子节点
s_index=[]#系统描述的id
s_father_deprel={}
for ele in e1:
    if ele['form']=="系统":
        s_index.append(ele["id"])
        s_father_deprel[ele["id"]]={}
        for i in range(len(ele["head"])):
            s_father_deprel[ele["id"]][ele["deprel"][i]]=ele["head"][i]
            #s_father_deprel实际上是{系统名：{'Pat': 2, 'Exp': 5}}

#用于保存用例图的数据结构
#{系统名:{actor:[usecase,usecase],actor:[usecase,usecase]}}
print("s_father_deprel:",s_father_deprel)
use_case_diagram_index={}
for s in s_index:
    for sk,sv in s_father_deprel.items():
        actor_index = 0
        for k, v in sv.items():
            # 用pat找actor

            if k == "Pat": # 对应的动词，是actor的动作
                for ele in e1:
                    if v in ele["head"] and "Agt" in ele["deprel"]:
                        #说明此时的ele节点是用户
                        actor_index=ele["id"]
                        print("actor_index0:",actor_index)
                        use_case_diagram_index[actor_index]=[]
            # 用exp当事关系找用例
            if k == "Exp":  # 对应的节点就是用例中的操作
                # 根据use_case_verb,找到相对应的名词，应该是cont，客事关系
                for ele in e1:
                    if v in ele["head"] and "Cont" in ele["deprel"]:
                        use_case_e = [v, ele["id"]]

                        if actor_index in use_case_diagram_index.keys():
                            use_case_diagram_index[actor_index].append(use_case_e)
                        else:
                            use_case_diagram_index[actor_index] = [use_case_e]


#根据数据结构输出最终用例：
use_case_diagram={}
print("use_case_diagram_index:",use_case_diagram_index)
for k,v in use_case_diagram_index.items():
    actor=e1[k-1]["form"]
    print(actor)
    use_case_list=[]
    for vv in v:
        use_case_verb=e1[vv[0]-1]["form"]
        use_case_noun=e1[vv[1]-1]["form"]
        use_case_list.append(use_case_verb+use_case_noun)
    use_case_diagram[actor]=use_case_list

print(use_case_diagram)



