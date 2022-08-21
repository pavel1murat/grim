#!/usr/bin/env python
#-------------------------------------------------------------------------------------------------
# takes fully expanded .FCL produced in --debug-config mode, generates an .org version of it
#
# call format: 
#               fcl_to_org.py --file=aaa.fcl [--verbose=level]
# 
# output     : aaa.org - org representation of the expanded fcl file
#
# verbose mode used only for internal debugging
#-------------------------------------------------------------------------------------------------
import argparse, sys, os, time

class Table:
    def __init__(self,name):
        self.fName     = name
        self.fDict     = {}

    def name(self):
        return self.fName;
   
class Sequence:
    def __init__(self,name):
        self.fName     = name
        self.fList     = []

    def name(self):
        return self.fName
   
#------------------------------------------------------------------------------
class Tool:

    def __init__(self):
        self.fFilename      = None
        self.fVerbose       = 0
        self.fTable         = Table('main')
# ---------------------------------------------------------------------
    def Print(self,Name,level,Message):
        if (level > self.fVerbose): return 0;
        now = time.strftime('%Y/%m/%d %H:%M:%S',time.localtime(time.time()))
        message = now+' [ GridTool::'+Name+' ] '+Message
        print(message)

#------------------------------------------------------------------------------
    def ParseParameters(self):
        name = 'ParseParameters'
        
        self.Print(name,2,'Starting')
        self.Print(name,2, '%s' % sys.argv)

        desc = 'fcl to org format converter: \n creates an ORG representation of the expanded FCL file.' + \
               ' The output .ORG file has the same name as the input .FCL file, just a different extension.'

        parser = argparse.ArgumentParser(description=desc)

        if (len(sys.argv) == 1):
            parser.print_help()
            sys.exit()

        parser.add_argument('--file'    , type=str, help='expanded .fcl file name', default = None)
        parser.add_argument('--verbose' , type=int, help='verbose'                , default = 0   )

        args = parser.parse_args()

        self.fFilename     = args.file
        self.fVerbose      = args.verbose

        return 

#------------------------------------------------------------------------------
    def parse_sequence(self,lines,ifirst,seq):
        if (self.fVerbose > 0): print('# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> parse_sequence:',seq.name())

        iend = -1;
        nlines=len(lines)

        i = ifirst

        while (i < nlines):
            iend = i
            line = lines[i].lstrip().rstrip()
            if (self.fVerbose > 0): print ('# parse_sequence line # %5i :'%i, line)
            if (line[0] == '#'): 
                i = iend+1
                continue;
            # assume that ']' or '],' is a separate line
            if (line[0] == ']'):
                # done
                if (self.fVerbose > 0): print('# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> end parse_sequence, i=',i);
                return i
            elif (line == '['):
                new_seq = Sequence('')
                seq.fList.append(new_seq);
                iend = self.parse_sequence(lines,i+1,new_seq)
                if (self.fVerbose > 0): print('# >>>>>>>>>>>>>>>>>>>>>>>>> back from parse_sequence, iend=',iend);
                
            elif (line == '{'):
                # unnamed table
                new_table = Table('')
                seq.fList.append(new_table);
                iend = self.parse_table(lines,i+1,new_table)
                if (self.fVerbose > 0): print('# >>>>>>>>>>>>>>>>>>>>>>>>> back from parse_table, iend=',iend);
                
            else:
                if (self.fVerbose > 0): print('# >>>>>>>>>>>> adding: ',line);
                seq.fList.append(line)
            
            i = iend+1

        return iend

#------------------------------------------------------------------------------
    def parse_table(self,lines,ifirst,table):
        if (self.fVerbose > 0): print('# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> parse_table:',table.name())

        iend   = ifirst;
        nlines = len(lines)
        seq    = None

        i = ifirst

        while (i < nlines):
            iend = i

            line = lines[i].lstrip().rstrip()
            if (self.fVerbose > 0): print ('# line # %5i :'%i, line)
            if (line[0] == '#'):                             
                i = i+1
                continue;
            s   = line.split();
            nw  = len(s)
            if (nw > 0) and (s[nw-1] == '{'): 
                #------------------------------------------------------------------------------
                # new table
                name = s[0].split(':')[0]
                if (self.fVerbose > 0): print( '# new table name:',name)
                new_table         = Table(name)
                table.fDict[name] = new_table
                iend              = self.parse_table(lines,i+1,new_table)
                # break
            elif (line[0] == '}'):
                #------------------------------------------------------------------------------
                # end table
                iend = i;
                break
            else:
            # just add something to the table
                words = line.split(':');
                nww   = len(words);
                if (nww > 1) :
                    nam   = words[0];
                    x     = words[1].lstrip().rstrip();
                    if (x == '['):
                        #----------
                        # sequence
                        seq = Sequence(nam)
                        table.fDict[nam] = seq
                        iend = self.parse_sequence(lines,i+1,seq)
                    else:
                        #--------------
                        # a simple line
                        table.fDict[nam] = words[1]
                else:
                    print ('>> ERROR: ',words)
            i = iend+1;

        if (self.fVerbose > 0): print('# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> end table:',table.name(),'line:',iend)
        return iend


#------------------------------------------------------------------------------
    def print_list_to_org(self,sequence,prefix,fout):

        for e in sequence.fList:
            if isinstance(e,Table) :
                fout.write(prefix+' table   : %-40s\n'%e.name())
                self.print_table_to_org(e,prefix+'*',fout)
            elif isinstance(e,Sequence):
                fout.write(prefix+' sequence: %-40s\n'%e.name())
                self.print_list_to_org(e,prefix+'*',fout)
            else:
                fout.write ('      %s\n'%e)

#------------------------------------------------------------------------------
    def print_table_to_org(self,table,prefix,fout):

        for k in table.fDict.keys():
            element = table.fDict[k]
            # print(prefix+'*  ',k, 'type:',type(element))
            # print (element)

            if isinstance(element,Table) :
                fout.write(prefix+' table   : %-40s\n'%k)
                self.print_table_to_org(element,prefix+'*',fout)
            elif isinstance(element,Sequence):
                fout.write(prefix+' sequence: %-40s\n'%k)
                self.print_list_to_org(element,prefix+'*',fout)
            else:
                # print ('>> element: ',element,type(element))
                fout.write('%s %s : %s\n'%(prefix,k,element));

#------------------------------------------------------------------------------
# check log files. asume they are copied into the output area
#------------------------------------------------------------------------------
    def parse_fcl(self,fn):
        name = 'parse_fcl'

        lines = open(fn).readlines();
        
        iend   = -1;
        nlines = len(lines);
        ifirst = 0;

        if (self.fVerbose > 0): print('# fn = %s nlines: %7i'%(fn,nlines));

        fn_out = fn.replace('.fcl','.org')

        fout = open(fn_out,'w')

        while (ifirst < nlines):
            iend  = self.parse_table(lines,ifirst,self.fTable)
            ifirst = iend+1;

        # at this point the table is parsed, we can print it in a form of .org file

        fout.write('# -*- mode:org -*-\n')
        fout.write('# printing output in org format:\n')

        self.print_table_to_org(self.fTable,'*',fout);

        fout.close()

#------------------------------------------------------------------------------
# main program, just make a GridSubmit instance and call its methods
#------------------------------------------------------------------------------
if (__name__ == '__main__'):

    x = Tool()
    x.ParseParameters()

    x.parse_fcl(x.fFilename)

    sys.exit(0);
