import re

#region global
r_dic={
    'add': '100000',
    'and': '100100',
    'sub': '100010',
    'nor': '100111',
    'or' : '100101',
    'slt': '101010'
}
i_dic={
    'addi': '001000',
    'lw'  : '100011',
    'sw'  : '101011',
    'beq' : '000100',
    'bne' : '000101'
}

reg_dic={
    '$zero': '00000',
    '$at'  : '00001',
    '$v0'  : '00010',
    '$v1'  : '00011',

    '$a0'  : '00100',
    '$a1'  : '00101',
    '$a2'  : '00110',
    '$a3'  : '00111', #7

    '$t0'  : '01000',
    '$t1'  : '01001',
    '$t2'  : '01010',

    '$t3'  : '01011',
    '$t4'  : '01100',
    '$t5'  : '01101',
    '$t6'  : '01110',
    '$t7'  : '01111',#15

    '$s0'  : '10000',
    '$s1'  : '10001',
    '$s2'  : '10010',

    '$s3'  : '10011',
    '$s4'  : '10100',
    '$s5'  : '10101',
    '$s6'  : '10110',
    '$s7'  : '10111',#23

    '$t8'  : '11000',
    '$t9'  : '11001',#25

    '$k0': '11010',
    '$k1': '11011',  # 27

    '$gp': '11100',  # 28
    '$sp': '11101', #29
    '$fp': '11110',  # 30
    '$ra': '11111',  # 30




}
label_dic = {}
value_dic={}

address_data=0
datacount=0

address_code=0
codecount=0

#endregion
def towscm(n):
    siz=15
    i=0
    m=""
    while(siz>=0):
        if(i==1):
           if n[siz]=='1':
               m += '0'
           else:
               m+='1'
        else:
            if(n[siz]=='1'):
                i+=1
                m+='1'

            else:
              m+='0'
        siz-=1
    siz=15
    converted=""
    while(siz>=0):
        converted+=m[siz]
        siz-=1



    return converted
#region functions

#region data
def getdata(line):
    global address_data
    global datacount
    lineParts=line.split()
    label_dic[lineParts[0]] = address_data

    if (lineParts[2] == ".space"):

        address_data += (4 * int(lineParts[3]))
        for i in range(0, int(lineParts[3])):
            with open("data.txt", "a") as machine_code:
                machine_code.write('MEMORY(%d) <= "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX" ;\n' % (datacount))
            datacount += 1

    elif (lineParts[2] == ".word"):

        parameters = lineParts[3].split(",")
        address_data += (4 * len(parameters))
        for param in parameters:
            with open("data.txt", "a") as machine_code:
                #label_dic[lineParts[0]] = address_data
                machine_code.write('MEMORY({}) <= "{:032b}" ;\n'.format(datacount, int(param)))
            datacount += 1

#endregion data

#region text
def getinstruction(line):
    global address_code
    global codecount

    if re.search(':',line):
        lineParts=line.split()
        label_dic[lineParts[0]] = address_code

    address_code += 4

def  r_machineCode(func,rd,rs,rt,count):
    no_rs=reg_dic[rs]
    no_rt=reg_dic[rt]
    no_rd=reg_dic[rd]

    with open("code.txt", "a") as machine_code:
        machine_code.write('MEMORY(%d) := "000000%s%s%s00000%s" ;\n' % (count, no_rs,no_rt,no_rd,func))

def i_machineCode(opcode, para0, para1, para2, count,current_address):

    if opcode=='001000':   #addi
        first=reg_dic[para1]
        second=reg_dic[para0]
        third=int(para2)        #hn7wlo binary

    elif opcode=='100011' or opcode=='101011': #lw , sw
        first=reg_dic[para2]
        second=reg_dic[para0]
        third=para1  #mmkn ykon label 2w rkm

        if third in label_dic.keys():
            res=label_dic[third]
        else:
            res=int(third)

        third=res

    elif opcode=='000100' or opcode=='000101': #be , bne
        first=reg_dic[para0]
        second=reg_dic[para1]
        third=para2     #label to jmp

        target = label_dic[third]
        res = int(target) - current_address
        print(current_address)
        print(int(target))
        if (res > 0):
            res = (res -4) / 4

        elif (res < 0):

            res = (res - 4) / 4
            res = res * -1
            ress="{:016b}".format(int(res))
            print(ress)
            res=towscm(ress)
            print(res)
            with open("code.txt", "a") as machine_code:
                machine_code.write('MEMORY({}) := "{}{}{}{}" ;\n'.format(count, opcode, first, second, res))
                return

        third=res

    with open("code.txt", "a") as machine_code:
        machine_code.write('MEMORY({}) := "{}{}{}{:016b}" ;\n'.format(count, opcode, first, second, int(third)))

def j_machineCode(opcode,label_address,count):
    if label_address in label_dic.keys():
        address = label_dic[label_address]/4

        with open("code.txt", "a") as machine_code:
            machine_code.write('MEMORY({}) := "{}{:026b}" ;\n'.format(count, opcode, int(address)))

    """else:
        print("error !!!!")
"""


def machineCode(line):
    global address_code
    global codecount

    lineParts=line.split()

    if re.search(':',line):
        startIndex=2
    else:
        startIndex=0

    if lineParts[startIndex] in r_dic.keys():
        value = r_dic[lineParts[startIndex]]
        parameters=lineParts[startIndex+1].split(',')
        """if parameters[0] not in reg_dic.keys():
            print("register name error in line: ", (codecount))
        elif parameters[1] not in reg_dic.keys():
            print("register name error in line: ", (codecount))
        elif parameters[2] not in reg_dic.keys():
            print("register name error in line: ", (codecount))
            
            
            """

        r_machineCode(value, parameters[0], parameters[1], parameters[2], codecount)

    elif lineParts[startIndex] in i_dic.keys():
        value = i_dic[lineParts[startIndex]]

        parameters = lineParts[startIndex + 1].split(',')

        i_machineCode(value, parameters[0], parameters[1], parameters[2], codecount,address_code)

    elif lineParts[startIndex]=='j':
        j_machineCode('000010', lineParts[startIndex + 1], codecount)

    else:
        print("instruction error in line: ",(codecount))

    codecount+=1
    address_code+=4


#endregion text

#endregion








#region main

#region reading file
list=[]
i=-1
file=open("os.txt","r")
for line in file:
    if re.search('#',line):
        parts=line.split('#')
        workingPart=parts[0]
        if workingPart!='' :
            workingPart = re.sub(' +', ' ', workingPart)
            workingPart = re.sub(' ?, ?', ',', workingPart)
            workingPart = re.sub(' ?\( ?', ',', workingPart)
            workingPart = re.sub(' ?\)', '', workingPart)
            workingPart = re.sub(' ?:', ' :', workingPart)
            if workingPart != ' ':
                i += 1
                list.append(workingPart)

    else:

        if re.search('\n', line):
            parts = line.split('\n')
            workingPart = parts[0]
            if workingPart != '':
                workingPart=re.sub(' +', ' ', workingPart)
                workingPart = re.sub(' ?, ?', ',', workingPart)
                workingPart = re.sub(' ?\( ?', ',', workingPart)
                workingPart = re.sub(' ?\)', '', workingPart)
                workingPart = re.sub(' ?:', ' :', workingPart)
                if workingPart != ' ':
                    i += 1
                    list.append(workingPart)

        else:
            workingPart=line
            workingPart = re.sub(' +', ' ', workingPart)
            workingPart = re.sub(' ?, ?', ',', workingPart)
            workingPart = re.sub(' ?\( ?', ',', workingPart)
            workingPart = re.sub(' ?\)', '', workingPart)
            workingPart = re.sub(' ?:', ' :', workingPart)
            if workingPart!=' ':
                i += 1
                list.append(workingPart)

    if re.search('.data',workingPart):
        dataIndex=i
    elif re.search('.text',workingPart):
        textIndex=i



file.close()
print(list)
print(dataIndex)
print(textIndex)
#endregion

#region data
for index in range(dataIndex+1,textIndex):
    getdata(list[index])

#endregion data

#region text
for index in range(textIndex+1,len(list)):
    getinstruction(list[index])

address_code=0
for index in range(textIndex+1,len(list)):
    machineCode(list[index])

#endregion text

#endregion main