import random

INSTRUCTIONS = ["举一个可能发现濒危动物物种的地方的例子。",
                "举一个回馈社区的公司的例子。",
                "说出一种通常作为宠物饲养的动物。",
                "说出一种既是酸又是碱的化学物质。",
                "说出一种印度菜。",
                "说出三种类型的机器学习算法。",
                "生成任何 5 个省钱技巧的列表。",
                "生成一个包含 5 项雨天户外活动的列表。",
                "描述墨西哥的首都。",
                "给出制作冰沙的三个步骤。"]

WEIGETS = [random.randint(1, 10) for _ in INSTRUCTIONS]

TGTFILE = 'realdata/sample.txt'

fin_list = []
for i in range(len(INSTRUCTIONS)):
    for _ in range(WEIGETS[i]):
        fin_list.append(INSTRUCTIONS[i])
random.shuffle(fin_list)

with open(TGTFILE, 'w') as f:
    for i in fin_list:
        f.write(i + '\n')
