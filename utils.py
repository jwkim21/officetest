import sys
import os

def file_open(open_file, open_type, fail_exit=True, __encoding__=None):    
    try:
        f=open(open_file, open_type, encoding=__encoding__, errors='ignore')
    except:        
        if fail_exit:
            print ("{0} open error.".format(open_file))
            sys.exit()
        else:            
            return 0
    return f

def load_to_list(open_file, open_type, split_sym=False, strip_sym=False, lower=False, fail_exit=True, __encoding__=None):
    f=file_open(open_file, open_type, fail_exit, __encoding__=__encoding__)
    if f==0:
        return []
    
    #a=f.read()
    #data=[]
    #line=f.readline()
    #data+=[line]
    #n=0
    #while line:
    #    line=f.readline()
    #    data+=[line]
    #    n+=1
    #data=data[:-1]
    data=f.readlines()
    modi_data=[]
    for d in data:
        dd=d.strip(' \r\n')
        if lower!=False:
            dd=dd.lower()
        if strip_sym!=False:
            dd=dd.strip(strip_sym)
        if split_sym!=False:
            dd=dd.split(split_sym)

        #skip empty line
        if dd!='':
            modi_data.append(dd)
    f.close()
    return modi_data

def dir_list(in_path, include_name=None, ext=None):
    file_list=os.listdir(in_path)
    flist=[]
    for i in file_list:
        flag=0        
        if include_name!=None and not include_name in i:
            flag=1
        if ext!=None and not ext in i[-(len(ext)):]:
            flag=1

        if flag==0 and ext!=None:
            flist.append(i[:-(len(ext))])
        elif flag==0:
            flist.append(i)

    flist.sort()
    return flist

def wer(ref, hyp , evaluation='correct', unit='char', debug=False):
    '''
    Calculation of WER with Levenshtein distance.
    '''

    SUB_PENALTY=1
    INS_PENALTY=1
    DEL_PENALTY=1

    if unit=='char':
        r=ref
        h=hyp        
    else:   #word ; space
        r = ref.split()
        h = hyp.split()
    #costs will holds the costs, like in the Levenshtein distance algorithm
    costs = [[0 for inner in range(len(h)+1)] for outer in range(len(r)+1)]
    # backtrace will hold the operations we've done.
    # so we could later backtrace, like the WER algorithm requires us to.
    backtrace = [[0 for inner in range(len(h)+1)] for outer in range(len(r)+1)]
 
    OP_OK = 0
    OP_SUB = 1
    OP_INS = 2
    OP_DEL = 3
     
    # First column represents the case where we achieve zero
    # hypothesis words by deleting all reference words.
    for i in range(1, len(r)+1):
        costs[i][0] = DEL_PENALTY*i
        backtrace[i][0] = OP_DEL
         
    # First row represents the case where we achieve the hypothesis
    # by inserting all hypothesis words into a zero-length reference.
    for j in range(1, len(h) + 1):
        costs[0][j] = INS_PENALTY * j
        backtrace[0][j] = OP_INS
     
    # computation
    for i in range(1, len(r)+1):
        for j in range(1, len(h)+1):
            if r[i-1] == h[j-1]:
                costs[i][j] = costs[i-1][j-1]
                backtrace[i][j] = OP_OK
            else:
                substitutionCost = costs[i-1][j-1] + SUB_PENALTY # penalty is always 1
                insertionCost    = costs[i][j-1] + INS_PENALTY   # penalty is always 1
                deletionCost     = costs[i-1][j] + DEL_PENALTY   # penalty is always 1
                 
                costs[i][j] = min(substitutionCost, insertionCost, deletionCost)
                if costs[i][j] == substitutionCost:
                    backtrace[i][j] = OP_SUB
                elif costs[i][j] == insertionCost:
                    backtrace[i][j] = OP_INS
                else:
                    backtrace[i][j] = OP_DEL
                 
    # back trace though the best route:
    i = len(r)
    j = len(h)
    numSub = 0
    numDel = 0
    numIns = 0
    numCor = 0
    history=[]
    if debug:
        print("OP\tREF\tHYP")
        lines = []
    while i > 0 or j > 0:        
        if backtrace[i][j] == OP_OK:
            numCor += 1
            i-=1
            j-=1
            log=['OK', r[i], h[j]]
            if debug:
                lines.append("OK\t" + r[i]+"\t"+h[j])
        elif backtrace[i][j] == OP_SUB:
            numSub +=1
            i-=1
            j-=1
            log=['SUB', r[i], h[j]]
            if debug:
                lines.append("SUB\t" + r[i]+"\t"+h[j])
        elif backtrace[i][j] == OP_INS:
            numIns += 1
            j-=1
            log=['INS', '*', h[j]]
            if debug:
                lines.append("INS\t" + "****" + "\t" + h[j])
        elif backtrace[i][j] == OP_DEL:
            numDel += 1
            i-=1
            log=['DEL', r[i], '*']
            if debug:
                lines.append("DEL\t" + r[i]+"\t"+"****")
        history.insert(0, log)

    acc =((len(r) - numSub - numDel - numIns) / float(len(r)))   #percentage
    corr=((len(r) - numSub - numDel) / float(len(r)))
    #adv_acc=((len(r) - numSub - (0.5*numDel) - (0.5*numIns)) / float(len(r)))
    #acc=((numSub + numDel + numIns) / float(len(r)))       #error rate
    #corr=((numSub + numDel) / float(len(r)))               #error rate
    if debug:
        lines = reversed(lines)
        for line in lines:
            print(line)
        print("#cor " + str(numCor))
        print("#sub " + str(numSub))
        print("#del " + str(numDel))
        print("#ins " + str(numIns))
        print("#n   " + str(len(r)))        
        print("#Acc " + str(round(acc,2)))
        print("#Corr " + str(round(corr,2)))
    
    if acc<0:
        acc=0
    if corr<0:
        corr=0
    if evaluation=='correct':
        #return (numSub + numDel) / (float) (len(r))     #Correct
        return corr
    elif evaluation=='accuracy':
        return acc
    elif evaluation=='fscore':
        if corr+acc==0:
            return 0
        else:            
            return 2*(corr*acc)/(corr+acc)
    elif evaluation=='acc.corr':
        return acc, corr
    elif evaluation=='detail':
        return acc, corr, history
    else:
        #return (numSub + numDel + numIns) / (float) (len(r))       #Accuracy
        return corr
    
    #wer_result = round( (numSub + numDel + numIns) / (float) (len(r)), 3)
    #return {'WER':wer_result, 'Cor':numCor, 'Sub':numSub, 'Ins':numIns, 'Del':numDel}