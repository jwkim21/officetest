import sys
import time
import random
import numpy as np
from utils import *

def textFileSplit_by_lineNum():
    arg_info='./test.inp'
    split_line=200      #separate point
    #enc_src='cp874'
    #enc_src='cp1250'
    #enc_src='cp949'
    #enc_src='cp1252'
    enc_src='cp1251'
    enc_dst=enc_src
    
    #enc_dst='utf-8'

    list_info=load_to_list(arg_info, 'r')
    in_path=list_info[0]
    out_path=list_info[1]
    file_list=list_info[2:]

    for i, file_name in enumerate(file_list):
        contents=load_to_list(in_path+file_name, 'r', __encoding__=enc_src)
        niter=int(len(contents)/split_line)+1
        st=0
        for j in range(niter):
            if j==niter-1:
                part_text=contents[st:]
            else:
                part_text=contents[st:st+split_line]

            out_file=out_path+file_name[:-4]+'_{:02d}'.format(j)+file_name[-4:]
            #out_file=out_path+file_name[:-4]+'-a{:02d}'.format(j+1)+'-name'+file_name[-4:]
            f=file_open(out_file, 'w', __encoding__=enc_dst)
            for k in range(len(part_text)):
                f.write(part_text[k]+'\n')
            f.close()
            st+=split_line
        print(file_name+' {} files Done\n'.format(niter))

def textClustering_by_wordUnit():
    # set input & output file name
    encoding='cp1251'

    in_file='./in/ukr.txt'
    out_file='./out/ukr.txt'

    # read input list file
    text_src=load_to_list(in_file, 'r', __encoding__=encoding)
    #text_tgt=list(reversed(text_src))
    text_tgt=text_src[:]

    # open output file
    fout = open(out_file, 'w', encoding=encoding, errors='ignore')
        
    acc_range=[60, 0]
    #1st; word unit. 2nd;char unit.
    all_text=[]
    for n, p in enumerate(acc_range): #accuracy set
        i=0; cnt=0;
        fout.write('---{}%\n'.format(p))
        while len(text_tgt)>i:
            nSame=0
            cluster_set=[]
            idx_pick=[]
            print('{:04d}/{:04d}({:04d}) {} : '.format(cnt, len(text_src), len(text_tgt), text_tgt[i].encode(encoding)), end='', flush=True)
            for j in range(len(text_tgt)):
                score=wer(text_tgt[i], text_tgt[j] , evaluation='accuracy', unit='word')
                #score=wer(text_tgt[i], text_tgt[j] , evaluation='accuracy', unit='char')

                if i==j:
                    continue       #self sentence

                if score==1:
                    nSame+=1
                    print('skip same sentence. n:{}, {}'.format(nSame, text_tgt[j].encode(encoding)))
                    #score=wer(text_tgt[i], text_tgt[j] , evaluation='fscore', unit='word')
                    
                if score >= p/100:
                    if len(cluster_set)==0:
                        cluster_set.append(text_tgt[i])
                        idx_pick.append(i)                    
                    cluster_set.append(text_tgt[j])
                    idx_pick.append(j)
            print('{}\n'.format(len(cluster_set)))
            if len(cluster_set)==0:
                i+=1
            else:
                #write
                for c in cluster_set:
                    fout.write('{}\n'.format(c))
                #del selected text
                for idx in reversed(sorted(idx_pick)):
                    if idx<i:
                        i-=1
                    del text_tgt[idx]

                ##debug
                #for c in cluster_set:
                #    if c in all_text:
                #        print(c)
                #        sys.exit()
                #all_text+=cluster_set
            cnt+=1

    fout.close()
    return 1

def deleteSameSent_from_file():    
    # set input & output file name
    encoding='cp949'

    input_list_file = './in/추가.txt'             #will add text
    input2_list_file = './in/org.txt'             #exist text
    output_text_file = './in/kor_result.txt'

    # read input list file
    modi_file1=load_to_list(input_list_file, 'r', __encoding__=encoding)
    modi_file2=load_to_list(input2_list_file, 'r', __encoding__=encoding)

    same_sent=[]
    for i in modi_file1:
        for n,j in enumerate(modi_file2):
            if i==j:
                same_sent+=[i]
                print(n, j)
                break

    print('[{}] same sentences.'.format(len(same_sent)))
    
    # open output file
    fout = open(output_text_file, 'w')

    if 1:
        #save differnt text
        for i in range(len(modi_file1)-1, -1, -1):
            if modi_file1[i] in same_sent:
                del modi_file1[i]
        for i in modi_file1:
            fout.write('{}\n'.format(i))

    else:
        #save same text
        for i in same_sent:
            fout.write('{}\n'.format(i))

    fout.close()

def deleteSameSent_whole_file():    
    import bisect
    # set input & output file name
    encoding='cp1251'

    input_list = 'x:/Ukr/db/wrnn_mila/script_make/'             #will add text
    #input_list='./same_in/'
    output_text = 'x:/Ukr/db/wrnn_mila/script_make/out/'
    ext_txt='.txt'

    filelist=dir_list(input_list, ext=ext_txt)
    #filelist=filelist[2400:]
    fullSent=[]
    del_sent=0
    for i, filename in enumerate(filelist):
        print('({}/{}). {}'.format(i+1, len(filelist), filename))
        sents=load_to_list(input_list+filename+ext_txt, 'r', __encoding__=encoding)
        
        if 1:       #single file
            re_sents=list(set(sents))
            nskip=len(sents)-len(re_sents)
            f_out=file_open(output_text+filename+ext_txt, 'w', __encoding__=encoding)
            for j, sent in enumerate(re_sents):
                f_out.write('{}\n'.format(sent))
            f_out.close()
            del_sent+=nskip
            print('\tdeleted:{}'.format(nskip))
        else:       #all files
            nskip=0
            print('\tIn list:{}'.format(len(fullSent)))
            #sents=list(set(sents))
            #fullSent=list(sorted(fullSent))
            f_out=file_open(output_text+filename+ext_txt, 'w', __encoding__=encoding)
            for j, sent in enumerate(sents):
                sent=sent.strip()
                idx=bisect.bisect(fullSent, sent)
                if len(fullSent)>0 and len(fullSent)>idx and fullSent[idx]==sent:
                    nskip+=1
                    continue
                else:

                    fullSent.insert(idx, sent)
                    f_out.write('{}\n'.format(sent))

            f_out.close()
            print('\tdeleted:{}'.format(nskip))
            del_sent+=nskip
    print('Deleted sentence : {}'.format(del_sent))

def FindTargetSent():
    #지정된 문장이 어떤 파일에 있는지 찾는 기능

    def replace_Text(src, sym):
        #just remove
        new_text=[]
        for i in src:
            for j in sym:
                i=i.replace(j, '')
            new_text+=[i]
        return new_text

    encoding='cp949'
    remove_symbol=[' ', '.', ',', '"', '?', '<', '>',]
    input_list_file = './in/target.txt'             #will add text
    ref_file = './ref/'             #exist text
    output_file = './out/text_result.txt'

    # read input list file
    target_text=load_to_list(input_list_file, 'r', __encoding__=encoding)
    target_text2=replace_Text(target_text, remove_symbol)

    source_text=[]
    ref_list=dir_list(ref_file)
    for i in ref_list:
        tmp=load_to_list(ref_file+i, 'r', __encoding__=encoding)
        source_text+=[replace_Text(tmp, remove_symbol)]

    pos_list=[]
    pos_full=[]
    for i, target in enumerate(target_text2):
        file_pos=[]
        for j, source in enumerate(source_text):
            if target in source:
                file_pos+=[ref_list[j]]
                pos_full+=[ref_list[j]]
            #else:
            #    #동일하지는 않지만 문장내에 포함되어 있음.
            #    for k in source:
            #        if target in k:
            #            file_pos+=[ref_list[j]]
            #            pos_full+=[ref_list[j]]

        pos_list+=[file_pos]

    pos_full=list(set(pos_full))
    pos_full.sort()

    f=open(output_file, 'w')
    for i, target in enumerate(target_text):
        #f.write('{}'.format(target))
        if len(pos_list[i])==0:
            f.write('{}'.format(target))
            f.write('\tUnknown\n')
        #else:
        #    f.write('\n')
    f.write('\n')
    for i in pos_full:
        f.write('{}\n'.format(i))
    f.close()
    return 1

def make_batch_for_AutoDB():
    #orderd file size
    nFiles=20
    input_list_file='./auto_in/list'
    out_path='./auto_out/'
    list_files=load_to_list(input_list_file, 'r')

    nArray= [[] for i in range(nFiles)]
    for i, v in enumerate(list_files):
        nArray[i%nFiles]+=[v]

    for i in range(nFiles):
        listname='list{:02d}'.format(i)
        workname='work{:02d}.bat'.format(i)        

        f_work=open(out_path+workname, 'w')
        f_work.write('text2corpus.exe text2corpus.inp {}\n'.format(listname))
        f_work.write('pause\n')
        f_work.close()

        f_list=open(out_path+listname, 'w')
        for j in nArray[i]:
            f_list.write('{}\n'.format(j))
        f_list.close()

    return 1

def line_header_attach():
    in_path='./in/auto/'
    out_path='./out/auto/'
    ext='.txt'
    encoding='cp949'

    filelist=dir_list(in_path,ext=ext)
    for nfile, filename in enumerate(filelist):
        in_file=in_path+filename+ext
        out_file=out_path+filename+ext
        contents=load_to_list(in_file, 'r', __encoding__=encoding)

        print('{}. {}'.format(nfile, filename))
        f=file_open(out_file, 'w', __encoding__=encoding)
        for nsent, sentence in enumerate(contents):
            f.write('{}. {}\n'.format(nsent+1, sentence))
    return 1

def txt_to_pdf():
    '''
    https://pyfpdf.readthedocs.io/en/latest/index.html
    '''

    from fpdf import FPDF
    in_path='./in/auto/'
    out_path='./out/auto/'
    ext_from='.txt'
    ext_to='.pdf'
    encoding='cp949'

    filelist=dir_list(in_path,ext=ext_from)
    for nfile, filename in enumerate(filelist):
        in_file=in_path+filename+ext_from
        out_file=out_path+filename+ext_to
        contents=load_to_list(in_file, 'r', __encoding__=encoding)

        print('{}. {}'.format(nfile, filename))

        pdf=FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=15)
        for nsent, sentence in enumerate(contents):
            pdf.cell(200, 10, txt='a', ln=1, align='L')
        pdf.output(out_file)

    return 1

def docx_to_text():
    '''
    https://stackoverflow.com/questions/25228106/how-to-extract-text-from-an-existing-docx-file-using-python-docx
    '''

    import docx
    in_path='./in/doc/'
    out_path='./out/doc/'
    ext_from='.docx'
    ext_to='.txt'
    encoding='cp949'

    filelist=dir_list(in_path,ext=ext_from)
    allText=[]
    for nfile, filename in enumerate(filelist):
        print(filename)
        in_file=in_path+filename+ext_from
        doc=docx.Document(in_file)
        fullText=[]
        speaker='[상담원]'
        for para in doc.paragraphs:
            atext=para.text
            atext=atext.strip()
            if len(atext)==0:
                continue

            if 1:       #domain
                #for multi line
                if '[상담원]' in atext:
                    speaker='[상담원]'
                elif '[고객]' in atext:
                    speaker='[고객]'

                if speaker=='[고객]':
                #if speaker=='[상담원]':
                    continue

                atext=atext.replace('[고객]', '')
                atext=atext.replace('[상담원]', '')
                atext=atext.strip()
                atext=atext.replace('. ', '.\n').split('\n')
                btext=[]
                for sent in atext:
                    sent=sent.strip()
                    if sent[-1]!='.' and sent[-1]!='?':
                        sent+='.'
                    btext+=[sent]
                fullText+=btext
            else:
                fullText.append(atext)

        fout=file_open(out_path+filename+ext_to, 'w', __encoding__=encoding)
        for i in fullText:
            fout.write('{}\n'.format(i))
        fout.close()
        allText+=fullText

    #purifyText=list(set(allText))
    purifyText=[]
    for text in allText:
        if text not in purifyText:
            purifyText+=[text]

    fout=file_open(out_path+'all'+ext_to, 'w', __encoding__=encoding)
    for i in purifyText:
        fout.write('{}\n'.format(i))
    fout.close()    

def symbol_addition_per_word():
    # set input & output file name
    encoding='cp949'

    input_list = './in/symbol/'             #will add text
    output_text = './out/symbol/'
    ext_txt='.txt'
    attach_symbol='#'

    MAX_NSYLL_SENT=60
    MAX_NSYLL_WORD=5

    filelist=dir_list(input_list, ext=ext_txt)

    for i, filename in enumerate(filelist):
        print('({}/{}). {}'.format(i+1, len(filelist), filename))
        sents=load_to_list(input_list+filename+ext_txt, 'r', __encoding__=encoding)

        f_out=file_open(output_text+filename+ext_txt, 'w', __encoding__=encoding)
        fullSent=[]
        for j, sent in enumerate(sents):
            sent=sent.strip()
            psent=sent.replace(' ', '')
            split_sent=sent.split(' ')

            symbol_pos=np.random.choice(len(split_sent))
            if len(psent)>MAX_NSYLL_SENT:
                continue
            #if len(split_sent)<=1:
            #    continue

            for k, word in enumerate(split_sent):
                pword=word.strip()
                pword=pword.rstrip('.')
                pword=pword.rstrip('?')
                pword=pword.rstrip('!')
                if len(pword)>MAX_NSYLL_WORD:
                    continue

                #for target position (symbol_pos)
                #if k!=symbol_pos:
                #    continue

                sent_symbol=''
                for l in range(len(split_sent)):
                    word_symbol=split_sent[l]
                    if k==l:
                        word_symbol='#'+word_symbol
                    if l>0:
                        word_symbol=' '+word_symbol

                    sent_symbol+=word_symbol                
                fullSent+=[sent_symbol]
                f_out.write('{}\n'.format(sent_symbol))
        f_out.close()
    print('Finished')

def symbol_addition_per_word_sort():
    # set input & output file name
    encoding='cp949'

    input_list = './in/symbol/'             #will add text
    output_text = './out/symbol/symbol.txt'
    ext_txt='.txt'
    attach_symbol='#'

    MAX_NSYLL_SENT=60
    MAX_NSYLL_WORD=5

    filelist=dir_list(input_list, ext=ext_txt)

    #classify sentence
    sent_classify=[ [] for i in range(5)]
    for i, filename in enumerate(filelist):
        print('({}/{}). {}'.format(i+1, len(filelist), filename))
        sents=load_to_list(input_list+filename+ext_txt, 'r', __encoding__=encoding)

        for j, sent in enumerate(sents):
            sent=sent.strip()
            psent=sent.replace(' ', '')
            split_sent=sent.split(' ')

            if len(psent)>MAX_NSYLL_SENT:
                continue

            if len(split_sent)>4:
                sent_classify[4]+=[sent]
            elif len(split_sent)>3:
                sent_classify[3]+=[sent]
            elif len(split_sent)>2:
                sent_classify[2]+=[sent]
            elif len(split_sent)>1:
                sent_classify[1]+=[sent]
            elif len(split_sent)>0:
                sent_classify[0]+=[sent]
            else:
                continue

    #balance sort
    fullText=[]
    percentage_sent=[3,7,15,25,50]
    while 1:
        nskip=0
        for narray in range(len(percentage_sent)):
            if len(sent_classify[narray])>percentage_sent[narray]:
                selections=np.random.choice(len(sent_classify[narray]), size=percentage_sent[narray], replace=False)
                for sel in selections:
                    fullText+=[sent_classify[narray][sel]]
                selections=sorted(selections, reverse=True)
                for sel in selections:
                    sent_classify[narray].pop(sel)
            else:
                nskip+=1
        if nskip==len(percentage_sent):
            break

    #symbol marking
    fullSent=[]
    for j, sent in enumerate(fullText):
            sent=sent.strip()
            psent=sent.replace(' ', '')
            split_sent=sent.split(' ')

            if len(split_sent)>5:
                nsym=3
            elif len(split_sent)>1:
                nsym=2
            else:
                nsym=1

            symbol_pos=np.random.choice(len(split_sent), size=nsym, replace=False)
            for k, word in enumerate(split_sent):
                pword=word.strip()
                pword=pword.rstrip('.')
                pword=pword.rstrip('?')
                pword=pword.rstrip('!')
                #if len(pword)>MAX_NSYLL_WORD:
                #    continue

                #for target position (symbol_pos)
                if k not in symbol_pos:
                    continue

                if len(split_sent)==1:
                    fullSent+=[sent]

                sent_symbol=''
                for l in range(len(split_sent)):
                    word_symbol=split_sent[l]
                    if k==l:
                        word_symbol='#'+word_symbol
                    if l>0:
                        word_symbol=' '+word_symbol

                    sent_symbol+=word_symbol                
                fullSent+=[sent_symbol]

    f_out=file_open(output_text, 'w', __encoding__=encoding)
    for i in fullSent:
        f_out.write('{}\n'.format(i))
    f_out.close()

    print('Finished')

def text_purify():
    in_path='d:/Code_python/json_extractor/CorpusOfAll/out/'
    out_path='./out/modu/'
    ext_txt='.txt'
    encoding='cp949'

    filelist=dir_list(in_path, ext=ext_txt)
    for nfile, filename in enumerate(filelist):
        print('{}/{}. {}'.format(nfile+1, len(filelist), filename))
        in_file=in_path+filename+ext_txt
        sents=load_to_list(in_file, 'r', __encoding__=encoding)
        fullText=[]
        for sent in sents:
            atext=sent.strip()
            atext=atext.replace('. ', '.\n')
            atext=atext.replace('? ', '?\n')
            atext=atext.replace('! ', '!\n')
            atext=atext.split('\n')
            if len(atext)==0:
                continue
            fullText+=atext            
        tmpText=[]
        for s, sent in enumerate(fullText):
            if sent not in tmpText:
                tmpText+=[sent]
            print('-> {} / {}'.format(s+1, len(fullText)), end='\r', flush=True)
        fullText=tmpText

        fout=file_open(out_path+filename+ext_txt, 'w', __encoding__=encoding)
        for i in fullText:
            fout.write('{}\n'.format(i))
        fout.close()
    print('Finished')

def linefeed_N_elementes():
    header=[0]
    in_list=[50, 2, 66, 10, 33, 21, 41, 45, 54, 37, 17, 75, 58, 81, 79, 25, 59, 82, 68, 14, 8, 30, 51, 5, 67, 13, 34, 22, 42, 46, 55, 38, 20, 76, 61, 84, 80, 26, 60, 83, 69, 15, 9, 31, 52, 3, 70, 11, 35, 43, 47, 56, 39, 18, 77, 62, 85, 23, 63, 86, 72, 6, 53, 4, 71, 12, 36, 44, 48, 57, 40, 19, 78, 65, 88, 24, 64, 87, 73, 7, 29, 32, 1, 74, 49, 16, 28, 27, 122, 96, 126, 98, 97, 112, 113, 106, 105, 131, 127, 99, 124, 133, 125, 134, 107, 115, 116, 103, 117, 114, 123, 111, 132, 90, 100, 108, 118, 129, 91, 94, 95, 89, 110, 120, 130, 104, 92, 102, 119, 93, 121, 101, 109, 128, ]
    max_num=206
    linechange=10
    digit_format='{:>3d}, '

    in_list=header+in_list
    if len(in_list)<max_num:
        add=[0 for i in range(max_num-len(in_list))]
        in_list+=add

    out_set=[]
    for n in range(0, len(in_list), linechange):
        sidx=n
        eidx=n+linechange
        out_set+=[in_list[sidx:eidx]]

    with open('tmp', 'w') as f:
        for i in out_set:
            for j in i:
                out_str=digit_format.format(j)
                f.write(out_str)
            f.write('\n')
    return 1

def element_combination():
    import itertools
    list_1=[ "", "만", "2만", "3만", "4만", "5만", "6만", "7만", "8만", "9만", "10만", "11만", "12만", "13만", "14만", "15만", "16만", "17만", "18만", "19만", "20만", ]
    list_2=[ "", "천", "2천", "3천", "4천", "5천", "6천", "7천", "8천", "9천", ]
    list_3=[ "", "백", "2백", "3백", "4백", "5백", "6백", "7백", "8백", "9백", ]
    list_4=[ "", "십", "2십", "3십", "4십", "5십", "6십", "7십", "8십", "9십", ]
    list_5=[ "", "1", "2", "3", "4", "5", "6", "7", "8", "9", ]

    with open('comb', 'w') as f:
        for i in range(210000):
            f.write('{}.\n'.format(i))
    sys.exit()
    #all_list=[list_1, list_2, list_3, list_4, list_5]
    comb=list(itertools.product(list_1, list_2, list_3, list_4, list_5))

    list_combination=[]
    for i in comb:
        i=list(i)        

        tmp=" ".join(i).strip()
        tmp=tmp.split()
        if len(tmp)>0:
            #if tmp[0]=='1만':
            #    tmp[0]='만'
            #elif tmp[0]=='1천':
            #    tmp[0]='천'
            #elif tmp[0]=='1백':
            #    tmp[0]='백'
            #elif tmp[0]=='1십':
            #    tmp[0]='십'
            tmp=" ".join(tmp).strip()
            list_combination.append(tmp)
    with open('comb', 'w') as f:
        for i in list_combination:
            f.write('{}.\n'.format(i))
    return 1

def IsInList(candidate, dest, nhead=1):
    #check english extended
    if len(dest)>1:
        if dest[0]=='e' and dest[1].isupper():
            dest=dest[1:]
    #check first latter
    if len(dest)>=nhead:
        dst=dest[:nhead]        
    else:
        dst=dest

    for n in candidate:
        if n in dst:
            flag=1
            break
        else:
            flag=0
    return flag
def phoneme_table_maker():
    in_dir='phone/in/'
    out_dir='phone/out/'
    lang='ukr'
    ext='.txt'
    phone_list=load_to_list(in_dir+lang+ext, 'r')

    #vowel
    #nasal:m n
    #stop:p b t d k g
    #affricate: ts tS dH
    #fricative:f v s z S H h
    #trill:r
    #approximant:l
    nasal=['N', 'M']
    stop=['P', 'B', 'D', 'K', 'G', 'T']
    affricate=['CH', 'TS']
    fricative=['F', 'V', 'S', 'Z', 'H', 'X', 'C']
    trill=['R']
    approximant=['L', 'J', 'W']
    voiced_sound=approximant+nasal

    phone_dict=[]
    non_stress_cnt=0
    non_stress_ph=[]
    prev_ph=''
    prev_ph_id=-1
    for i, ph in enumerate(phone_list):
        ph_dict=dict()
        ph_dict['phone_stress']=ph
        ph_dict['id_stress']=i+1        
        if ph[-1].isdigit():            
            ph_dict['phone']=ph[:-1]
            ph_dict['vowel']=1
            ph_dict['class']=0
            ph_dict['accent']=int(ph[-1])
            if prev_ph!=ph_dict['phone']:
                non_stress_cnt+=1
                ph_dict['id_cc']=ph_dict['id_stress']
                prev_ph_id=ph_dict['id_stress']
            else:
                ph_dict['id_cc']=prev_ph_id
        else:
            ph_dict['phone']=ph
            ph_dict['vowel']=0
            ph_dict['class']=1
            ph_dict['accent']=0
            non_stress_cnt+=1
            ph_dict['id_cc']=ph_dict['id_stress']
            prev_ph_id=ph_dict['id_stress']
        ph_dict['id']=non_stress_cnt
        
        isvoiced=IsInList(voiced_sound, ph)        
        if isvoiced or ph_dict['vowel']:
            ph_dict['voiced']=1
        else:
            ph_dict['voiced']=0

        #kind
        #vowel
        if ph_dict['vowel']:
            ph_dict['kind']=1
        #voiced
        elif ph_dict['voiced']:
            ph_dict['kind']=2
        #voiced consonant
        #silence
        #unvoiced
        else:
            ph_dict['kind']=4

        #class
        if IsInList(nasal, ph):
            ph_dict['class']=1
        elif IsInList(affricate, ph, nhead=2):
            ph_dict['class']=3
        elif IsInList(stop, ph):
            ph_dict['class']=2
        elif IsInList(fricative, ph):
            ph_dict['class']=4
        elif IsInList(trill, ph):
            ph_dict['class']=5
        elif IsInList(approximant, ph):
            ph_dict['class']=6
        else:
            ph_dict['class']=0

        prev_ph=ph_dict['phone']        
        phone_dict+=[ph_dict]

    f=open(out_dir+lang+ext, 'w')
    f.write('symbol_stress\tid_stress\tsymbol\tid\tvowel\tvoiced\taccent\tCC\tLC\tRC\tLCMerge\tRCMerge\tclass\tkind\n')
    for i, ph in enumerate(phone_dict):
        f.write('{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(ph['phone_stress'], ph['id_stress'], ph['phone'], ph['id'], ph['vowel'], ph['voiced'], ph['accent'], ph['id_cc'], ph['id_cc'], ph['id_cc'], ph['id_cc'], ph['id_cc'], ph['class'], ph['kind']))
    f.close()

    #non-stress
    f=open(out_dir+lang+'_nonstress'+ext, 'w')
    f.write('symbol\tid\n')
    prev_ph=''
    for i, ph in enumerate(phone_dict):
        if prev_ph!=ph['phone']:
            f.write('{}\t{}\n'.format(ph['phone'], ph['id']))
        prev_ph=ph['phone']
    f.close()
    a=1

def collection_sentences():
    # set input & output file name
    encoding='cp1251'

    mode_select='lineByline'
    #mode_select='random'

    byline=15
    input_file = './in/ukr.txt'
    output_file = './out/ukr.txt'

    # read input list file
    text_sents=load_to_list(input_file, 'r', __encoding__=encoding)    

    # open output file
    fout = open(output_file, 'w', encoding=encoding)
    cnt=0
    if mode_select=='lineByline':
        for i in range(0, len(text_sents), byline):
            fout.write('{}\n'.format(text_sents[i]))
            cnt+=1

    fout.close()
    print('{} -> {} sentences.'.format(len(text_sents), cnt))

    return 1
if __name__ == "__main__":
    print('git testing')
    #라인 갯수로 분리
    #textFileSplit_by_lineNum()

    #같은 문장 삭제
    #deleteSameSent_from_file()

    #전체 파일에서 중복 문장 제거
    #deleteSameSent_whole_file()

    #N번째(혹은 랜덤) 문장 선택
    #collection_sentences()
    
    #단어단위 유사문장 분류
    #textClustering_by_wordUnit()

    #지정된 문장이 어떤 파일에 있는지 찾는 기능
    #FindTargetSent()

    #AutoDB batch file 만들기
    #make_batch_for_AutoDB()

    #line 숫자 맨 처음에 출력
    #line_header_attach()

    #txt to pdf
    #txt_to_pdf()

    #docx to text
    #docx_to_text()

    #단어 별로 특정 표시되는 문장 만들기(make sentence for emphasis)
    #symbol_addition_per_word()
    #symbol_addition_per_word_sort()

    #문장 단위 분리
    #text_purify()

    #리스트 10개 단위로 나누기(phoneset 정리)
    #linefeed_N_elementes()

    #N개 리스트 모든 조합 만들기
    #element_combination()

    #새언어 제작시 음소 테이블표
    #phoneme_table_maker()
    sys.exit()

